'''
Created on Jun 9, 2014

@author: yutelin
'''
import json
from models import Node
import ConfigParser
import os
from constants import FILENAME_STATE_CFG, STR_LAST_NODE_TIMESTAMP, STR_TIMESTAMP,\
    STR_NODE

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
            m_node = Node(ip_address=node[STR_NODE], timestamp=node[STR_TIMESTAMP])
            self.session.add(m_node)
            add_count = add_count + 1
            if m_node.timestamp > new_last_node_timestamp : new_last_node_timestamp = m_node.timestamp 
        self.session.commit()
        
        # 4. Update new last node timestamp
        if add_count > 0 : 
            self.__update_last_node_timestamp__(new_last_node_timestamp)
            print "Update last node timestamp to:", new_last_node_timestamp