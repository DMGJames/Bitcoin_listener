'''
Created on Jun 9, 2014

@author: yutelin
'''
import os
from os.path import sys
import getopt
from node_pusher import NodePusher
import ConfigParser
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker


def set_env():
    #1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)

def set_session():    
    #2. Load db config
    file_dir = os.path.dirname(os.path.realpath(__file__))
    db_config_file = os.path.join(file_dir, "alembic.ini")
    config = ConfigParser.ConfigParser()
    config.read(db_config_file)
    
    #3. Set SQLAlchemy db engine
    db_engine = config.get('alembic', 'sqlalchemy.url')
    
    #4. Configure SQLAlchemy session
    engine = create_engine(db_engine)
    session = sessionmaker()
    session.configure(bind=engine)
    return session()
    
def get_opt(argv):
    inputfile = ''   
    try:
        opts, _ = getopt.getopt(argv,"hn:",["ifile="])
    except getopt.GetoptError:
        print 'main.py -n <nodefile> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'main.py -n <nodefile> '
            sys.exit()
        elif opt in ("-n"):
            inputfile = arg
    return inputfile
   
def update_db_nodes(node_file, session):
    node_pusher = NodePusher(session=session)
    node_pusher.update_db_nodes(file_path = node_file)
   
if __name__ == '__main__':
    set_env()
    node_file = get_opt(sys.argv[1:])
    session = set_session()
    update_db_nodes(node_file = node_file, session = session)
    session.close()
    