#!/usr/bin/env python
'''
Created on Jun 17, 2014

@author: yutelin
'''
import os
from os.path import sys
from constants import NODE_PINGER_DAEMON_LOG_DIR, NODE_PINGER_DAEMON_STDOUT,\
    NODE_PINGER_DAEMON_STDERR, NODE_PINGER_DAEMON_PID_FILE
from node_pinger import NodePinger
from utils.daemon_utils import Daemon
import time
from common import set_session

class NodePingerDaemon(Daemon):
    def set_session(self, session):
        self.session = session
        
    def run(self):
        print "start NodePinger"
        node_pinger = NodePinger(session = self.session)
        while True:
            try:
                node_pinger.update_db_all_node_activities()
            except Exception, e:
                print "Error on node_pinger.update_db_all_node_activities():", e
            time.sleep(1)
            print "next round"
        print "end NodePinger"
        
def set_env():
    #1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)
    
    #2. Create logging dir
    if not os.path.exists(NODE_PINGER_DAEMON_LOG_DIR):
        os.makedirs(NODE_PINGER_DAEMON_LOG_DIR)

if __name__ == '__main__':
    set_env()
    if len(sys.argv) == 3:
        env_setting = sys.argv[2]
        daemon = NodePingerDaemon(pidfile=NODE_PINGER_DAEMON_PID_FILE, 
                              stdout=NODE_PINGER_DAEMON_STDOUT, 
                              stderr=NODE_PINGER_DAEMON_STDERR)
        session = set_session(env_setting=env_setting)
        daemon.set_session(session = session)
        if 'start' == sys.argv[1]:
            print "start"
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print "stop"
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print "restart"
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart local|test|prod" % sys.argv[0]
        sys.exit(2)
