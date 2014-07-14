#!/usr/bin/env python
'''
Created on Jul 11, 2014

@author: yutelin
'''
##### Set environment #####
import os
from os.path import sys
import time
def set_env_1():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)
    sys.path.append(file_dir+"/../")
set_env_1()    
########################################################################

from utils.daemon_utils import Daemon
from constants import TX_ADDR_INFO_UPDATE_DAEMON_LOG_DIR, TX_ADDR_INFO_UPDATE_DAEMON_PID_FILE,\
    TX_ADDR_INFO_UPDATE_DAEMON_STDOUT, TX_ADDR_INFO_UPDATE_DAEMON_STDERR
from common import set_session
from tx.transaction_address_info_updater import TransactionAddressInfoUpdater

class TransactionAddrInfoUpdaterProcessDaemon(Daemon):
    def set_session(self, query_session, update_session):
        self.query_session = query_session
        self.update_session = update_session
        
    def run(self):
        print "Start TransactionAddrInfoUpdaterProcessDaemon"
        updater_process = TransactionAddressInfoUpdater(query_session=self.query_session, update_session = self.update_session)
        while(True):
            updater_process.start()
            time.sleep(600) # 10 minutes
        print "End TransactionAddrInfoUpdaterProcessDaemon"

def set_env_2():
    #2. Create logging dir
    if not os.path.exists(TX_ADDR_INFO_UPDATE_DAEMON_LOG_DIR):
        os.makedirs(TX_ADDR_INFO_UPDATE_DAEMON_LOG_DIR) 
        
if __name__ == '__main__':
    set_env_2()
    if len(sys.argv) == 3:
        env_setting = sys.argv[2]
        daemon = TransactionAddrInfoUpdaterProcessDaemon(pidfile=TX_ADDR_INFO_UPDATE_DAEMON_PID_FILE, 
                              stdout=TX_ADDR_INFO_UPDATE_DAEMON_STDOUT, 
                              stderr=TX_ADDR_INFO_UPDATE_DAEMON_STDERR)
        query_session = set_session(env_setting=env_setting)
        update_session = set_session(env_setting=env_setting)
        daemon.set_session(query_session = query_session, update_session = update_session)
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