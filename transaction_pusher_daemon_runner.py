#!/usr/bin/env python
'''
Created on Jun 19, 2014

@author: yutelin
'''
from transaction_pusher import TransactionPusher
from utils.daemon_utils import Daemon
import os
from os.path import sys
from constants import TX_PUSHER_DAEMON_PID_FILE, TX_PUSHER_DAEMON_STDOUT,\
    TX_PUSHER_DAEMON_STDERR, TX_PUSHER_DAEMON_LOG_DIR
from common import set_session

class TransactionPusherDaemon(Daemon):
    def set_session(self, session):
        self.session = session
        
    def run(self):
        print "Start TransactionPusherDaemon"
        pusher = TransactionPusher(session = self.session)
        pusher.start()
        print "End TransactionPusherDaemon"

def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)

    #2. Create logging dir
    if not os.path.exists(TX_PUSHER_DAEMON_LOG_DIR):
        os.makedirs(TX_PUSHER_DAEMON_LOG_DIR)
        
if __name__ == '__main__':
    set_env()
    if len(sys.argv) == 3:
        env_setting = sys.argv[2]
        daemon = TransactionPusherDaemon(pidfile=TX_PUSHER_DAEMON_PID_FILE, 
                              stdout=TX_PUSHER_DAEMON_STDOUT, 
                              stderr=TX_PUSHER_DAEMON_STDERR)
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