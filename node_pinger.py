#!/usr/bin/env python
'''
Created on Jun 16, 2014

@author: yutelin
'''
from bitnodes.protocol import Connection
import socket
import os
import ConfigParser
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
import sys
from models import Node, NodeActivity
from constants import STR_ACTIVE, STR_INACTIVE, PINGER_POOL_SIZE, STR_IP_ADDRESS,\
    STR_PORT, STR_STATUS, STR_ADDRESS
import threading
import threadpool
import time

def is_node_active(ip_address, port):
    connection = Connection((ip_address, port))
    result = True
    try:
        connection.open()
        handshake_msgs = connection.handshake()
        if len(handshake_msgs) == 0:
            result = False
        else: 
            connection.ping()
            # Sink received messages to flush them off socket buffer
            try:
                pong_mesg = connection.get_messages()
                if len(pong_mesg) == 0: result = False
            except socket.timeout as err:
                result = False
                print "Socket timeout:", err
    except socket.error as err:
        result = False
        print "Error:(", ip_address,"): ", err
    except Exception, e:
        result = False
        print "Error:", e
    connection.close()
    print "is_node_active \"%s\": %s" % (ip_address, result)
    return result


def set_env():
    #1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)
    
def set_session(env_setting='local'):    
    #2. Load db config
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file_name = "alembic_%s.ini" % env_setting
    db_config_file = os.path.join(file_dir, file_name)
    config = ConfigParser.ConfigParser()
    config.read(db_config_file)
    
    #3. Set SQLAlchemy db engine
    db_engine = config.get('alembic', 'sqlalchemy.url')
    
    #4. Configure SQLAlchemy session
    engine = create_engine(db_engine)
    session = sessionmaker()
    session.configure(bind=engine)
    return session()

def __test_ping__():
    ip = "107.170.211.10"
    port = 8333
    is_active = is_node_active(ip, port)
    print "%s:%i is active: %s" % (ip, port, is_active)
    
    ip = '1.0.0.1'
    is_active = is_node_active(ip, port)
    print "%s:%i is active: %s" % (ip, port, is_active)
 
def __test_db_query__(session):
    nodes = session.query(Node).filter(Node.user_agent.isnot(None)).add_columns(Node.user_agent, Node.ip_address, Node.port)
    count = 0
    for node in nodes:
        print node
        print "is live:", is_node_active(node.ip_address, node.port)
        count = count+1
    print "count:", count
  
def __test_node_pinger__(session):
    ip = "107.170.211.10"
    port = 8333 
    pinger = NodePinger(session = session)
    node = {STR_IP_ADDRESS : ip, STR_PORT : port} 
    pinger.update_db_node_activity(node)
       
class NodePinger():
    def __init__(self, session):
        self.session = session
        self.lock = threading.Lock()
        self.pool = threadpool.ThreadPool(PINGER_POOL_SIZE)
        
    def __get_last_node_activity_record__(self, address):
        self.lock.acquire(True)
        try:
            result = session.query(NodeActivity).filter(NodeActivity.address == address).\
                add_columns(NodeActivity.address, NodeActivity.status).\
                order_by(NodeActivity.created_at.desc()).first()
            result = result.__dict__ if result else None
        except Exception, e:
            print "Exception on getting last activity:", e
        self.lock.release()
        return result
        
    def __get_all_sanity_nodes__(self):
        result = session.query(Node).filter(Node.user_agent.isnot(None)).\
            add_columns(Node.user_agent, Node.ip_address, Node.port, Node.address)
        return result

    def __boolean_to_activity_string__(self, active = False):
        return STR_ACTIVE if active else STR_INACTIVE     
        
    def update_db_node_activity(self, node):
        #1. Get last record
        last_activity = self.__get_last_node_activity_record__(address = node.get(STR_ADDRESS))
        
        #2. Get status
        is_active = is_node_active(ip_address = node.get(STR_IP_ADDRESS), port = node.get(STR_PORT))
        is_active_str = self.__boolean_to_activity_string__(is_active)
        
        #3. Update database
        if not last_activity or not is_active_str == last_activity.get(STR_STATUS):
            node_activity = NodeActivity(address = node.get(STR_ADDRESS),
                                          status = is_active_str)
            self.lock.acquire(True)
            try: 
                self.session.add(node_activity)
                self.session.commit()
            except Exception, e:
                print "Exception on adding NodeActivity:", e
                self.seesion.rollback()
            self.lock.release()
            print "%s changed status to: %s" % (node.get(STR_IP_ADDRESS), is_active_str)
        else :
            print "%s keeps status: \"%s\"" % (node.get(STR_IP_ADDRESS), is_active_str)
        
    def update_db_all_node_activities(self):
        #1. Load all nodes
        nodes = self.__get_all_sanity_nodes__()
        
        #2. Update them with multi-thread. Using this form of multi-threading is because
        ### the nodes are loaded in a lazy fashion. We don't want to fetch the whole table
        ### in a single query.   
        for node in nodes:
            node_dict = node.__dict__
            while self.pool._requests_queue.qsize() > len(self.pool.workers) :
                time.sleep(0.5)
            requests = threadpool.makeRequests(self.update_db_node_activity, [node_dict])
            for req in requests: self.pool.putRequest(req)
            
        
if __name__ == '__main__':
    set_env()
    env_setting = sys.argv[1]
    print "Environment:" ,env_setting
    session = set_session(env_setting=env_setting)
#     __test_ping__()
#     __test_db_query__(session = session)
#     __test_node_pinger__(session = session)
    node_pinger = NodePinger(session = session)
    node_pinger.update_db_all_node_activities()
    session.close()
