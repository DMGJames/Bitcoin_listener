from sqlalchemy import Column, DateTime, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import BigInteger


Base = declarative_base()
 
class Node(Base):
    __tablename__   = 'node'
    #id              = Column(Integer, primary_key=True)
    address         = Column(String(250),primary_key=True) # ip_address + port
    ip_address      = Column(String(250),nullable=False, index=True)
    timestamp       = Column(BigInteger, nullable=False, index=True)
    port            = Column(Integer,  nullable=False)
    city            = Column(String(250), index=True)
    start_height    = Column(BigInteger, index=True)
    country         = Column(String(250), index=True)
    hostname        = Column(String(250), index=True)
    time_zone       = Column(String(250), index=True)
    longitude       = Column(Numeric(precision=11, scale=8), index=True)
    latitude        = Column(Numeric(precision=10, scale=8), index=True) #http://stackoverflow.com/questions/12504208/what-mysql-data-type-should-be-used-for-latitude-longitude-with-8-decimal-places
    version         = Column(Integer, index=True)
    user_agent      = Column(String(250), index=True)
    org             = Column(String(250), index=True)
    asn             = Column(String(250), index=True)
    created_at      = Column(DateTime, default=func.now())    
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())
    
class NodeActivity(Base):
    __tablename__   = 'node_activity'
    id              = Column(Integer, primary_key=True)
    ip_address      = Column(String(250), index=True)
    status          = Column(String(250), index=True)
    created_at      = Column(DateTime, default=func.now(),index=True)
    