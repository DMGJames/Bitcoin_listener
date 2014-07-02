from sqlalchemy import Column, DateTime, Integer, String, Numeric, Text, Boolean
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
    address         = Column(String(250), index=True)
    status          = Column(String(250), index=True)
    created_at      = Column(DateTime, default=func.now(),index=True)
    
class Transaction(Base):
    __tablename__   = 'transaction'
    txid            = Column(String(250),primary_key=True)
    value           = Column(Numeric(precision=15, scale=8), index=True)
    created_at      = Column(DateTime, default=func.now(),index=True)
    block_height    = Column(Integer, index=True)
    has_multisig    = Column(Boolean, index=True)
    has_nulldata    = Column(Boolean, index=True)
    has_pubkey      = Column(Boolean, index=True)
    has_pubkeyhash  = Column(Boolean, index=True)
    has_scripthash  = Column(Boolean, index=True)

    def print_pushing_message(self):
        print "Pushed transaction:", self.txid
    
class TransactionInfo(Base):
    __tablename__   = "transaction_info"
    #id              = Column(Integer, primary_key=True)
    txid            = Column(String(250), primary_key=True)
    relayed_from    = Column(String(250), primary_key=True)
    received_at     = Column(DateTime,index=True)
    created_at      = Column(DateTime, default=func.now(),index=True)
    json_string     = Column(Text)

    def print_pushing_message(self):
        print "Pushed transaction info:", self.txid, self.relayed_from
