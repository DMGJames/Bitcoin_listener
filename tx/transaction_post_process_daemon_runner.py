'''
Created on Jul 1, 2014

@author: yutelin
'''
##### Set environment #####
import os
from os.path import sys
def set_env_1():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)
    sys.path.append(file_dir+"/../")
set_env_1()    
########################################################################

from utils.daemon_utils import Daemon
from constants import TX_POST_DAEMON_LOG_DIR, TX_POST_DAEMON_PID_FILE,\
    TX_POST_DAEMON_STDOUT, TX_POST_DAEMON_STDERR
from common import set_session
from tx.transaction_post_process import TransactionPostProcess

class TransactionPostProcessDaemon(Daemon):
    def set_session(self, query_session, update_session):
        self.query_session = query_session
        self.update_session = update_session
        
    def run(self):
        print "Start TransactionPostProcessDaemon"
        post_process = TransactionPostProcess(query_session=self.query_session, update_session = self.update_session)
        post_process.run_post_process()
        print "End TransactionPostProcessDaemon"

def set_env_2():
    #2. Create logging dir
    if not os.path.exists(TX_POST_DAEMON_LOG_DIR):
        os.makedirs(TX_POST_DAEMON_LOG_DIR) 
        
if __name__ == '__main__':
    set_env_2()
    if len(sys.argv) == 3:
        env_setting = sys.argv[2]
        daemon = TransactionPostProcessDaemon(pidfile=TX_POST_DAEMON_PID_FILE, 
                              stdout=TX_POST_DAEMON_STDOUT, 
                              stderr=TX_POST_DAEMON_STDERR)
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