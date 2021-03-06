'''
Created on Jun 19, 2014

@author: yutelin
'''
import os
import sys
import ConfigParser
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
import time, calendar
from datetime import datetime

old_stdout = sys.stdout
class StdoutWithTimestamp:
    nl = True

    def write(self, x):
        if self.nl == True:
            old_stdout.write('%s %s' % (str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")), x))
        else:
            old_stdout.write(x)

        if x.endswith('\n'):
            self.nl = True
        else:
            self.nl = False

sys.stdout = StdoutWithTimestamp()


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
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()

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

def get_epoch_time():
    return calendar.timegm(time.gmtime())
