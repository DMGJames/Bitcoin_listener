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
from common import set_session
from patch.add_transaction_type import AddTransactionTypePatch
from constants import TX_PATCH_DAEMON_LOG_DIR, TX_PATCH_DAEMON_PID_FILE,\
    TX_PATCH_DAEMON_STDOUT, TX_PATCH_DAEMON_STDERR

class AddTransactionTypeDaemon(Daemon):
    def set_session(self, session):
        self.session = session
        
    def run(self):
        print "Start AddTransactionTypeDaemon"
        patch = AddTransactionTypePatch(session=self.session)
        patch.run_patch()
        print "End AddTransactionTypeDaemon"

def set_env_2():
    #2. Create logging dir
    if not os.path.exists(TX_PATCH_DAEMON_LOG_DIR):
        os.makedirs(TX_PATCH_DAEMON_LOG_DIR) 
        
if __name__ == '__main__':
    set_env_2()
    if len(sys.argv) == 3:
        env_setting = sys.argv[2]
        daemon = AddTransactionTypeDaemon(pidfile=TX_PATCH_DAEMON_PID_FILE, 
                              stdout=TX_PATCH_DAEMON_STDOUT, 
                              stderr=TX_PATCH_DAEMON_STDERR)
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