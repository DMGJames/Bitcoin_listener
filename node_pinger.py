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
from constants import ATTRIBUTE_ACTIVE, ATTRIBUTE_INACTIVE, DEFAULT_PINGER_POOL_SIZE, ATTRIBUTE_IP_ADDRESS, \
    ATTRIBUTE_PORT, ATTRIBUTE_STATUS
import threading
import threadpool
import time
import MySQLdb
import traceback
from common import set_session

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
        sys.stdout.write('E')
        # print "Error:(", ip_address, "): ", err
    except Exception, e:
        result = False
        print "Error:", e
    connection.close()
    #print "is_node_active \"%s\": %s" % (ip_address, result)
    sys.stdout.write('.')
    sys.stdout.flush()
    return result


def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)

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
        count = count + 1
    print "count:", count
  
def __test_node_pinger__(session):
    ip = "107.170.211.10"
    port = 8333 
    pinger = NodePinger(session=session)
    node = {ATTRIBUTE_IP_ADDRESS : ip, ATTRIBUTE_PORT : port} 
    pinger.update_db_node_activity(node)
       
class NetworkActivity():
    
    def __init__(self, ip_address, port, status):
        self.ip_address = ip_address
        self.port = port
        self.status = status
    
class NodePinger():
    def __init__(self, session):
        self.session = session
        self.lock = threading.Lock()
        self.pool = threadpool.ThreadPool(DEFAULT_PINGER_POOL_SIZE)
        self.activities = []
        
    def __get_last_node_activity_record__(self, address):
        self.lock.acquire(True)
        try:
            result = self.session.query(NodeActivity).filter(NodeActivity.address == address).\
                add_columns(NodeActivity.address, NodeActivity.status).\
                order_by(NodeActivity.created_at.desc()).first()
            result = result.__dict__ if result else None
        except (AttributeError, MySQLdb.OperationalError), e:
            print "Exception on getting last activity: MySQL operation error", e
            time.sleep(0.5)
        except Exception, e:
            print "Exception on getting last activity:", e
        finally:
            self.session.close()
        self.lock.release()
        return result
        
    def __get_all_sanity_nodes__(self):
        result = []
        try:
            result = self.session.query(Node).filter(Node.user_agent.isnot(None)).\
                add_columns(Node.user_agent, Node.ip_address, Node.port, Node.address)
            #result = [{ATTRIBUTE_ADDRESS: node.address, ATTRIBUTE_IP_ADDRESS:node.ip_address, ATTRIBUTE_PORT:node.port} for node in nodes]
        except Exception ,e:
            print e
        finally:
            self.session.close()
        return result

    def __boolean_to_activity_string__(self, active=False):
        return ATTRIBUTE_ACTIVE if active else ATTRIBUTE_INACTIVE     
        
    def update_db_node_activity(self, node):
        # 1. Get status
        is_active = is_node_active(ip_address=node.get(ATTRIBUTE_IP_ADDRESS), port=node.get(ATTRIBUTE_PORT))
        is_active_str = self.__boolean_to_activity_string__(is_active)
        
        # 2. Add NetworkActivity to the shared list self.activities
        activity = NetworkActivity(ip_address = node.get(ATTRIBUTE_IP_ADDRESS), port = node.get(ATTRIBUTE_PORT), status = is_active_str)
        self.lock.acquire(True)
        self.activities.append(activity)
        self.lock.release()

    def __update_db_with_activities__(self, activities):
        if activities:
            print "\n\n================================[Update db]:", len(activities)
            try:
                add_count = 0
                for activity in activities:
                    address = "%s:%s" % (activity.ip_address, activity.port)
                    #1. Get last status
                    last_activity = self.__get_last_node_activity_record__(address=address)
                    if not last_activity or not activity.status == last_activity.get(ATTRIBUTE_STATUS):
                        print "Add: ", activity.ip_address, activity.status
                        node_activity = NodeActivity(address=address,status=activity.status)
                        # Add to DB
                        self.session.add(node_activity)
                        self.session.commit()
                        add_count = add_count+1
                print "Added activities:", add_count 
            except Exception, e:
                print "Error on __update_db_with_activities__:", e
                traceback.print_exc(file=sys.stdout)
                self.session.rollback()
            finally:
                self.session.close()

            
    def update_db_all_node_activities(self):
        try:
            # 1. Load all nodes
            nodes = self.__get_all_sanity_nodes__()
            
            # 2. Update them with multi-thread. Using this form of multi-threading is because
            # ## the nodes are loaded in a lazy fashion. We don't want to fetch the whole table
            # ## in a single query.   
            for node in nodes:
                node_dict = node.__dict__
                while self.pool._requests_queue.qsize() > len(self.pool.workers) :
                    self.pool.wait()
                    self.__update_db_with_activities__(self.activities)
                    self.activities = []
                requests = threadpool.makeRequests(self.update_db_node_activity, [node_dict])
                for req in requests: self.pool.putRequest(req)
        except Exception, e:
            print "Exception on running \"update_db_all_node_activities\":", e
        
if __name__ == '__main__':
    set_env()
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    session = set_session(env_setting=env_setting)
#     __test_ping__()
#     __test_db_query__(session = session)
#     __test_node_pinger__(session = session)
    node_pinger = NodePinger(session=session)
    node_pinger.update_db_all_node_activities()
#     session.close()
