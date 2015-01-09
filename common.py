'''
Created on Jun 19, 2014

@author: yutelin
'''
import os
import sys
import ConfigParser
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

def set_session(env_setting='local'):    
    # 2. Load db config
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file_name = "alembic_%s.ini" % env_setting
    db_config_file = os.path.join(file_dir, file_name)
    config = ConfigParser.ConfigParser()
    config.read(db_config_file)
    
    # 3. Set SQLAlchemy db engine
    db_engine = config.get('alembic', 'sqlalchemy.url')
    
    # 4. Configure SQLAlchemy session
    engine = create_engine(db_engine)
    session_maker = sessionmaker()
    session_maker.configure(bind=engine)
    session = session_maker()
    return session

def get_hostname_or_die():
    try:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(file_dir, "HOSTNAME")
        with open(file_path, "r") as file:
            return file.readline().strip()
    except IOError:
        sys.exit("ERROR: hostname not found")
    except:
        unexpected_error()

def unexpected_error():
    sys.exit("UNEXPECTED ERROR: %s" % sys.exc_info()[0])

class SignalSystemExit(SystemExit):
    pass
