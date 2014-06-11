'''
Created on Jun 9, 2014

@author: yutelin
'''
import json
from models import Node
import ConfigParser
import os
from constants import FILENAME_STATE_CFG, STR_LAST_NODE_TIMESTAMP, STR_TIMESTAMP,\
    STR_NODE, STR_COUNTRY, STR_HOSTNAME, STR_LATITUDE, STR_LONGITUDE,\
    STR_START_HEIGHT, STR_TIME_ZONE, STR_USER_AGENT, STR_VERSION, STR_ASN,\
    STR_ORG, STR_CITY
import node_resolver

class NodePusher(object):
    '''
    classdocs
    '''

    def __init__(self, session):
        '''
        Constructor
        '''
        self.session = session
        
    def update_db_nodes(self, file_path):
        '''
        Load node files and update database
        '''
        print "Update database nodes: ", file_path
        fin = open(file_path, 'r')
        
        # 1. Parse Nodes
        nodes = []
        for line in fin:
            try:
                node_dict = json.loads(line)
                nodes.append(node_dict)
            except ValueError:
                pass
                #print "ValueError:", line, " (ignored)"
                
        # 2. Update db        
        self.__update_db_with_nodes__(nodes = nodes)        
        
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
            
    def __update_db_with_nodes__(self, nodes = []):     
        # 1. Get last timestamp from DB
        last_node_timestamp = self.__get_last_node_timestamp__()
        print "Upload nodes modified after:", last_node_timestamp
        
        # 2. filter old nodes
        nodes = [node for node in nodes if node[STR_TIMESTAMP] > last_node_timestamp]
        print "To upload nodes: "
        print json.dumps(nodes, indent=4)
        
        # 3. Update db with nodes
        new_last_node_timestamp = 0
        add_count = 0
        for node in nodes:
            ip_address, port = self.__split_address_and_port__(node[STR_NODE])
            node_data = node_resolver.get_node_info(address = ip_address, port = port)
            m_node = Node(ip_address            = ip_address,
                          port                  = port,  
                          timestamp             = node[STR_TIMESTAMP],
                          asn                   = node_data[STR_ASN],
                          city                  = node_data[STR_CITY],
                          country               = node_data[STR_COUNTRY],
                          hostname              = node_data[STR_HOSTNAME],
                          latitude              = node_data[STR_LATITUDE],
                          longitude             = node_data[STR_LONGITUDE],
                          org                   = node_data[STR_ORG],       
                          start_height          = node_data[STR_START_HEIGHT],
                          time_zone             = node_data[STR_TIME_ZONE],
                          user_agent            = node_data[STR_USER_AGENT], 
                          version               = node_data[STR_VERSION])
            #self.session.add(m_node)
            # print m_node.__dict__
            self.session.merge(m_node)
            add_count = add_count + 1
            if m_node.timestamp > new_last_node_timestamp : new_last_node_timestamp = m_node.timestamp 
        self.session.commit()
        
        # 4. Update new last node timestamp
        if add_count > 0 : 
            self.__update_last_node_timestamp__(new_last_node_timestamp)
            print "Update last node timestamp to:", new_last_node_timestamp