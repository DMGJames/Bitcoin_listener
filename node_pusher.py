'''
Created on Jun 12, 2014

@author: yutelin
'''
import os
import json
import ConfigParser
import redis
from constants import STR_DISCOVERED_NODES, NODE_LOADING_BATCH_SIZE,\
    STR_NODE_DISCOVERED, STR_CHANNEL, STR_TYPE, STR_MESSAGE, RESOLVING_POOL_SIZE,\
    MAI_REDIS_PASSWORD, DEFAULT_LOADING_BATCH_SIZE, DEFAULT_SLEEP_TIME,\
    FILENAME_STATE_CFG, STR_LAST_NODE_TIMESTAMP, STR_TIMESTAMP,\
    STR_NODE, STR_COUNTRY, STR_HOSTNAME, STR_LATITUDE, STR_LONGITUDE,\
    STR_START_HEIGHT, STR_TIME_ZONE, STR_USER_AGENT, STR_VERSION, STR_ASN,\
    STR_ORG, STR_CITY, STR_NODE_DATA, STR_IP_ADDRESS, STR_PORT
import node_resolver
import math
import time
import gevent
import threading
import threadpool
from models import Node
from pusher import Pusher


class NodePusher(Pusher):
    def __init__(self, session,
                 channel = STR_NODE_DISCOVERED,
                 queue = STR_DISCOVERED_NODES,
                 batch_size = DEFAULT_LOADING_BATCH_SIZE,
                 sleep_time = DEFAULT_SLEEP_TIME,
                 password = MAI_REDIS_PASSWORD):
        super(NodePusher, self).__init__(
            session = session,
            channel = channel,
            queue = queue,
            batch_size = batch_size,
            sleep_time = sleep_time,
            password = password)
        self.lock = threading.Lock()
        self.pool = threadpool.ThreadPool(RESOLVING_POOL_SIZE)

    def process_data(self, node_ips):
        current_timestamp = int(math.floor(time.time()))
        timed_node_ips = [{STR_NODE:node_ip, STR_TIMESTAMP:current_timestamp} for node_ip in node_ips]

        # 1. Get last timestamp from DB
        last_node_timestamp = self.__get_last_node_timestamp__()
        print "Upload nodes modified after:", last_node_timestamp
        
        # 2. filter old nodes
        timed_node_ips = [timed_node_ip for timed_node_ip in timed_node_ips if timed_node_ip[STR_TIMESTAMP] > last_node_timestamp]
        print "To upload nodes: "
        print json.dumps(timed_node_ips, indent=4)
        
        # 3. Download node data
        workers = [gevent.spawn(self.__set_node_data__, timed_node_ip) for timed_node_ip in timed_node_ips]
        gevent.joinall(workers)

        # 4. Update db with nodes
        new_last_node_timestamp = 0
        add_count = 0
        nodes = []
        for timed_node_ip in timed_node_ips:
            if timed_node_ip.get(STR_IP_ADDRESS): 
                node = self.__create_node__(timed_node_ip)
                nodes.append(node)
                add_count = add_count + 1
                if node.timestamp > new_last_node_timestamp : new_last_node_timestamp = node.timestamp

        # 5. Update new last node timestamp
        if add_count > 0 : 
            self.__update_last_node_timestamp__(new_last_node_timestamp)
            print "Update last node timestamp to:", new_last_node_timestamp

        return nodes

    def __create_node__(self, timed_node_ip):
        node_data = timed_node_ip.get(STR_NODE_DATA, {})
        result = Node(address      = timed_node_ip.get(STR_NODE),
                      ip_address   = timed_node_ip.get(STR_IP_ADDRESS),
                      port         = timed_node_ip.get(STR_PORT),  
                      timestamp    = timed_node_ip.get(STR_TIMESTAMP),
                      asn          = node_data.get(STR_ASN),
                      city         = node_data.get(STR_CITY),
                      country      = node_data.get(STR_COUNTRY),
                      hostname     = node_data.get(STR_HOSTNAME),
                      latitude     = node_data.get(STR_LATITUDE),
                      longitude    = node_data.get(STR_LONGITUDE),
                      org          = node_data.get(STR_ORG),
                      start_height = node_data.get(STR_START_HEIGHT),
                      time_zone    = node_data.get(STR_TIME_ZONE),
                      user_agent   = node_data.get(STR_USER_AGENT), 
                      version      = node_data.get(STR_VERSION))
        return result

    def __get_last_node_timestamp__(self):
        result = 0
        #1. Load state config
        file_dir = os.path.dirname(os.path.realpath(__file__))
        state_config_file = os.path.join(file_dir, FILENAME_STATE_CFG)
        if os.path.isfile(state_config_file):
            config = ConfigParser.ConfigParser()
            config.read(state_config_file)
            result = config.get(STR_NODE, STR_LAST_NODE_TIMESTAMP)
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
        if not config.has_section(STR_NODE): config.add_section(STR_NODE)
        #3. Update timestamp value
        config.set(STR_NODE, STR_LAST_NODE_TIMESTAMP, timestamp)
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
        ip_address, port = self.__split_address_and_port__(node[STR_NODE])
        print "set node data: ", ip_address, port
        node_data = node_resolver.get_node_info(address = ip_address, port = port)
        node[STR_NODE_DATA] = node_data
        node[STR_IP_ADDRESS] = ip_address
        node[STR_PORT] = port
        print "done: ", ip_address, port, node

"""
if __name__ == '__main__':
    #nodes = load_nodes()
    loader = NodeLoader()
    nodes = loader.load_nodes()
    print nodes
"""
    