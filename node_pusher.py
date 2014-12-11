'''
Created on Jun 12, 2014

@author: yutelin, webber
'''
import os
import json
import ConfigParser
from constants import DEFAULT_NODE_QUEUE,\
    DEFAULT_NODE_CHANNEL, DEFAULT_RESOLVING_POOL_SIZE,\
    DEFAULT_MAI_REDIS_PASSWORD, DEFAULT_LOADING_BATCH_SIZE, DEFAULT_SLEEP_TIME,\
    FILENAME_STATE_CFG, ATTRIBUTE_LAST_NODE_TIMESTAMP, ATTRIBUTE_TIMESTAMP,\
    ATTRIBUTE_NODE, ATTRIBUTE_COUNTRY, ATTRIBUTE_HOSTNAME, ATTRIBUTE_LATITUDE, ATTRIBUTE_LONGITUDE,\
    ATTRIBUTE_START_HEIGHT, ATTRIBUTE_TIME_ZONE, ATTRIBUTE_USER_AGENT, ATTRIBUTE_VERSION, ATTRIBUTE_ASN,\
    ATTRIBUTE_ORG, ATTRIBUTE_CITY, ATTRIBUTE_NODE_DATA, ATTRIBUTE_IP_ADDRESS, ATTRIBUTE_PORT
import node_resolver
import math
import time
import gevent
from models import Node
from pusher import Pusher
from common import set_session, get_hostname_or_die
import sys
from psutil_wrapper import PsutilWrapper
import gc

def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)
    
class NodePusher(Pusher):
    def __init__(self, session,
                 channel = DEFAULT_NODE_CHANNEL,
                 queue = DEFAULT_NODE_QUEUE,
                 batch_size = DEFAULT_LOADING_BATCH_SIZE,
                 sleep_time = DEFAULT_SLEEP_TIME,
                 password = DEFAULT_MAI_REDIS_PASSWORD,
                 pool_size = DEFAULT_RESOLVING_POOL_SIZE):
        super(NodePusher, self).__init__(
            session = session,
            channel = channel,
            queue = queue,
            batch_size = batch_size,
            sleep_time = sleep_time,
            password = password,
            pool_size = pool_size)

    def start(self):
        print "Node pusher started"
        sys.stdout.flush()
        super(NodePusher, self).start()

    def process_data(self, data):
        ps = PsutilWrapper(os.getpid())
        node_ips = data
        current_timestamp = int(math.floor(time.time()))
        timed_node_ips = [{ATTRIBUTE_NODE:node_ip, ATTRIBUTE_TIMESTAMP:current_timestamp} for node_ip in node_ips]

        # 1. Get last timestamp from DB
        last_node_timestamp = self.__get_last_node_timestamp__()
        print "Upload nodes modified after:", last_node_timestamp
        sys.stdout.flush()

        # 2. filter old nodes
        timed_node_ips = [timed_node_ip for timed_node_ip in timed_node_ips if timed_node_ip[ATTRIBUTE_TIMESTAMP] > last_node_timestamp]
        print "To upload nodes: "
        print json.dumps(timed_node_ips, indent=4)
        sys.stdout.flush()
        
        # 3. Download node data
        workers = [gevent.spawn(self.__set_node_data__, timed_node_ip) for timed_node_ip in timed_node_ips]
        gevent.joinall(workers)

        # 4. Update db with nodes
        new_last_node_timestamp = 0
        add_count = 0
        nodes = []
        for timed_node_ip in timed_node_ips:
            if timed_node_ip.get(ATTRIBUTE_IP_ADDRESS): 
                node = self.__create_node__(timed_node_ip)
                nodes.append(node)
                add_count = add_count + 1
                if node.timestamp > new_last_node_timestamp : new_last_node_timestamp = node.timestamp

        # 5. Update new last node timestamp
        if add_count > 0 : 
            self.__update_last_node_timestamp__(new_last_node_timestamp)
            print "Update last node timestamp to:", new_last_node_timestamp
            sys.stdout.flush()

        #print "# of unreachable objects:", gc.collect()
        #print gc.garbage

        return nodes

    def __create_node__(self, timed_node_ip):
        node_data = timed_node_ip.get(ATTRIBUTE_NODE_DATA, {})
        result = Node(address=timed_node_ip.get(ATTRIBUTE_NODE),
                      ip_address=timed_node_ip.get(ATTRIBUTE_IP_ADDRESS),
                      port=timed_node_ip.get(ATTRIBUTE_PORT),
                      timestamp=timed_node_ip.get(ATTRIBUTE_TIMESTAMP),
                      asn=node_data.get(ATTRIBUTE_ASN),
                      city=node_data.get(ATTRIBUTE_CITY),
                      country=node_data.get(ATTRIBUTE_COUNTRY),
                      hostname=node_data.get(ATTRIBUTE_HOSTNAME),
                      latitude=node_data.get(ATTRIBUTE_LATITUDE),
                      longitude=node_data.get(ATTRIBUTE_LONGITUDE),
                      org=node_data.get(ATTRIBUTE_ORG),
                      start_height=node_data.get(ATTRIBUTE_START_HEIGHT),
                      time_zone=node_data.get(ATTRIBUTE_TIME_ZONE),
                      user_agent=node_data.get(ATTRIBUTE_USER_AGENT),
                      version=node_data.get(ATTRIBUTE_VERSION),
                      pushed_from=get_hostname_or_die())
        return result

    def __get_last_node_timestamp__(self):
        result = 0
        #1. Load state config
        file_dir = os.path.dirname(os.path.realpath(__file__))
        state_config_file = os.path.join(file_dir, FILENAME_STATE_CFG)
        if os.path.isfile(state_config_file):
            config = ConfigParser.ConfigParser()
            config.read(state_config_file)
            result = config.get(ATTRIBUTE_NODE, ATTRIBUTE_LAST_NODE_TIMESTAMP)
        return int(result)
    
    def __update_last_node_timestamp__(self, timestamp):
        file_dir = os.path.dirname(os.path.realpath(__file__))
        state_config_file = os.path.join(file_dir, FILENAME_STATE_CFG)
        config = ConfigParser.ConfigParser()
        #1. Try to read the config file
        try:
            config.read(state_config_file)
        except:
            pass
        #2. Add section if not appeared
        if not config.has_section(ATTRIBUTE_NODE): config.add_section(ATTRIBUTE_NODE)
        #3. Update timestamp value
        config.set(ATTRIBUTE_NODE, ATTRIBUTE_LAST_NODE_TIMESTAMP, timestamp)
        with open(state_config_file, 'w') as configfile:
            config.write(configfile)
        
    def __split_address_and_port__(self, address):
        ip = None
        port = None
        if address and address.rfind(':') > 0:
            ip = address [:address.rfind(':')]
            port = int(address[address.rfind(':')+1:])
        else :
            ip = address
        return (ip, port)
    
    def __set_node_data__(self, node):
        ip_address, port = self.__split_address_and_port__(node[ATTRIBUTE_NODE])
        print "set node data: ", ip_address, port
        sys.stdout.flush()
        node_data = node_resolver.get_node_info(address=ip_address, port=port)
        node[ATTRIBUTE_NODE_DATA] = node_data
        node[ATTRIBUTE_IP_ADDRESS] = ip_address
        node[ATTRIBUTE_PORT] = port
        print "done: ", ip_address, port, node

    def __print_loading_message__(self, loaded):
        print "Done loading nodes"
        sys.stdout.flush()

    def __print_pushing_message__(self,  pushed):
        print "Done pushing nodes"
        sys.stdout.flush()

if __name__ == '__main__':
    set_env()
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    sys.stdout.flush()
    session = set_session(env_setting=env_setting)
    pusher = NodePusher(session=session, batch_size=5, pool_size=200, sleep_time=10)
    pusher.start()
