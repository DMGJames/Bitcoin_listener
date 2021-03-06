#!/usr/bin/env python
'''
Created on Jun 9, 2014

@author: yutelin
'''
import os
from os.path import sys
import getopt
from node_pusher import NodePusher
from common import set_session

env_setting = "local"

def set_env():
    #1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)
    
def get_opt(argv):
    inputfile = '' 
    env = 'local'  
    try:
        opts, _ = getopt.getopt(argv,"hn:e:",["ifile="])
    except getopt.GetoptError:
        print 'main.py -n <nodefile> -e local|prod|test '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'main.py -n <nodefile> -e local|prod|test'
            sys.exit()
        elif opt in ("-n"):
            inputfile = arg
        elif opt in ("-e") and arg in ['prod', 'test', 'local']:
            env = arg
    return inputfile, env
   
def update_db_nodes(node_file, session):
    if os.path.exists(node_file):
        node_pusher = NodePusher(session=session)
        node_pusher.update_db_nodes(file_path = node_file)
    else :
        pusher = NodePusher(session=session)
        pusher.start()

if __name__ == '__main__':
    set_env()
    (node_file, env) = get_opt(sys.argv[1:])
    env_setting = env
    session = set_session()
    update_db_nodes(node_file = node_file, session = session)
    session.close()
    