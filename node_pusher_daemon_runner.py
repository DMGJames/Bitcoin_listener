#!/usr/bin/env python
'''
Created on Jun 15, 2014

@author: yutelin
'''
from utils.daemon_utils import Daemon
from node_pusher import NodePusher
import os
import sys
import ConfigParser
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from constants import NODE_PUSHER_DAEMON_PID_FILE, NODE_PUSHER_DAEMON_STDOUT,\
    NODE_PUSHER_DAEMON_STDERR, NODE_PUSHER_DAEMON_LOG_DIR
from node_loader import NodeLoader

class NodePusherDaemon(Daemon):
    def set_session(self, session):
        self.session = session
        
    def run(self):
        node_pusher = NodePusher(session=self.session)
        print "start load_and_push_nodes"
        node_loader = NodeLoader()
        node_loader.load_and_push_nodes(node_pusher = node_pusher)
        print "end load_and_push_nodes"
        
def set_env():
    #1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)
    
    #2. Create logging dir
    if not os.path.exists(NODE_PUSHER_DAEMON_LOG_DIR):
        os.makedirs(NODE_PUSHER_DAEMON_LOG_DIR)

def set_session(env_setting='local'):    
    #2. Load db config
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file_name = "alembic_%s.ini" % env_setting
    db_config_file = os.path.join(file_dir, file_name)
    config = ConfigParser.ConfigParser()
    config.read(db_config_file)
    
    #3. Set SQLAlchemy db engine
    db_engine = config.get('alembic', 'sqlalchemy.url')
    
    #4. Configure SQLAlchemy session
    engine = create_engine(db_engine)
    session = sessionmaker()
    session.configure(bind=engine)
    return session()

if __name__ == '__main__':
    set_env()
    if len(sys.argv) == 3:
        env_setting = sys.argv[2]
        daemon = NodePusherDaemon(pidfile=NODE_PUSHER_DAEMON_PID_FILE, 
                              stdout=NODE_PUSHER_DAEMON_STDOUT, 
                              stderr=NODE_PUSHER_DAEMON_STDERR)
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

    session.close()