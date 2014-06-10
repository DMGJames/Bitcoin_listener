from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import BigInteger


Base = declarative_base()
 
class Node(Base):
    __tablename__   = 'node'
    id              = Column(Integer, primary_key=True)
    ip_address      = Column(String(250), nullable=False, index=True)
    timestamp       = Column(BigInteger, nullable=False, index=True)
    created_at      = Column(DateTime, default=func.now())    
