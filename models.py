from sqlalchemy import Column, DateTime, Integer, String, Numeric, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.sql.schema import Index
from sqlalchemy.dialects import mysql

Base = declarative_base()

class AddressTag(Base):
    __tablename__   = 'address_tag'
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer)
    tag             = Column(String(250))
    address         = Column(String(250), index=True)
    source          = Column(String(250), index=True)
    link            = Column(String(250))
    verified        = Column(Boolean)
    created_at      = Column(DateTime, default=func.now())
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())
 
class Node(Base):
    __tablename__   = 'node'
    #id              = Column(Integer, primary_key=True)
    address         = Column(String(250),primary_key=True, index=True) # ip_address + port
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
    pushed_from     = Column(String(25), index=True)
    created_at      = Column(DateTime, default=func.now())
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())

class NodeActivity(Base):
    __tablename__   = 'node_activity'
    id              = Column(Integer, primary_key=True, index=True)
    address         = Column(String(250), index=True)
    status          = Column(String(250), index=True)
    pushed_from     = Column(String(25), index=True)
    created_at      = Column(DateTime, default=func.now(),index=True)

class Transaction(Base):
    __tablename__   = 'transaction'
    txid            = Column(String(250),primary_key=True, index=True)
    value           = Column(Numeric(precision=15, scale=8), index=True)
    created_at      = Column(DateTime, default=func.now(),index=True)
    block_height    = Column(Integer, index=True)
    block_hash      = Column(String(250), index=True)
    has_multisig    = Column(Boolean, index=True)
    has_nulldata    = Column(Boolean, index=True)
    has_pubkey      = Column(Boolean, index=True)
    has_pubkeyhash  = Column(Boolean, index=True)
    has_scripthash  = Column(Boolean, index=True)
    pushed_from     = Column(String(25), index=True)

    def print_pushing_message(self):
        print "Pushed transaction:", self.txid

class TransactionInfo(Base):
    __tablename__   = "transaction_info"
    #id              = Column(Integer, primary_key=True)
    txid            = Column(String(250), primary_key=True, index=True)
    relayed_from    = Column(String(250), primary_key=True, index=True)
    received_at     = Column(DateTime,index=True)
    created_at      = Column(DateTime, default=func.now(),index=True)
    json_string     = Column(Text)
    pushed_from     = Column(String(25), index=True)

    def print_pushing_message(self):
        print "Pushed transaction info:", self.txid, self.relayed_from

class TransactionOutput(Base):
    __tablename__   = "transaction_vout"
    txid            = Column(String(250), primary_key=True, index=True)
    offset          = Column(Integer, primary_key=True, autoincrement=False, index=True)
    address         = Column(String(250), index=True)
    block_hash      = Column(String(250), index=True)
    block_height    = Column(Integer, index=True)
    value           = Column(Numeric(precision=15, scale=8), index=True)
    is_from_coinbase= Column(Boolean, index=True)

    def print_pushing_message(self):
        print "Pushed transaction vout:", self.txid, self.offset, self.address

Index('ix_transaction_output_txid_and_offset', TransactionOutput.txid, TransactionOutput.offset)

class TransactionInput(Base):
    __tablename__   = "transaction_vin"
    txid            = Column(String(250), primary_key=True, index=True)
    offset          = Column(Integer, primary_key=True, autoincrement=False, index=True)
    block_hash      = Column(String(250), index=True)
    block_height    = Column(Integer, index=True)
    output_txid     = Column(String(250), index=True) #TransactionOutput txid
    vout_offset     = Column(Integer, index=True) #TransactionOuput offset

    def print_pushing_message(self):
        print "Pushed transaction vin:", self.txid, self.offset, self.output_txid, self.vout_offset

Index('ix_transaction_input_output_txid_and_vout_index', TransactionInput.output_txid, TransactionInput.vout_offset)

class TransactionAddressInfo(Base):
    __tablename__   = "transaction_address_info"
    address         = Column(String(250), primary_key=True, index=True)
    received_value  = Column(Numeric(precision=15, scale=8), index=True)
    spent_value     = Column(Numeric(precision=15, scale=8), index=True)
    balance         = Column(Numeric(precision=15, scale=8), index=True)
    vin_count       = Column(Integer, index=True)
    vout_count      = Column(Integer, index=True)
    coinbase        = Column(Integer, index=True, default=0)

    def print_pushing_message(self):
        print "Pushed transaction address info:", self.address

class TransactionAddressInfoUpdate(Base):
    __tablename__   = "transaction_address_info_update"
    block_height    = Column(Integer, primary_key=True, index=True)
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())


class Block(Base):
    __tablename__   = "blocks"
    id              = Column(mysql.BIGINT, primary_key=True)
    hash            = Column(mysql.BINARY(32))
    time            = Column(mysql.BIGINT)
    received_time   = Column(mysql.BIGINT)
    relayed_by      = Column(mysql.VARBINARY(16))

class Transaction(Base):
    __tablename__   = "transactions"
    id              = Column(mysql.BIGINT, primary_key=True)
    hash            = Column(mysql.BINARY(32))
    block_id        = Column(mysql.BIGINT)
    received_time   = Column(mysql.BIGINT)
    fee             = Column(mysql.BIGINT)
    total_out_value = Column(mysql.BIGINT)
    num_inputs      = Column(mysql.INTEGER)
    num_outputs     = Column(mysql.INTEGER)
    coinbase        = Column(mysql.BIT)
    lock_time       = Column(mysql.BIGINT)
    relayed_by      = Column(mysql.VARBINARY(16))

class Input(Base):
    __tablename__   = "inputs"
    id              = Column(mysql.BIGINT, primary_key=True)
    output_id       = Column(mysql.BIGINT)
    script_type     = Column(mysql.TINYINT(unsigned=True))
    address_id      = Column(mysql.BIGINT)
    value           = Column(mysql.BIGINT)
    tx_id           = Column(mysql.BIGINT)
    offset          = Column(mysql.INTEGER)

class Output(Base):
    __tablename__   = "outputs"
    id              = Column(mysql.BIGINT, primary_key=True)
    script_type     = Column(mysql.TINYINT(unsigned=True))
    address_id      = Column(mysql.BIGINT)
    value           = Column(mysql.BIGINT)
    tx_id           = Column(mysql.BIGINT)
    offset          = Column(mysql.INTEGER)
    spent           = Column(mysql.BIT)

class Address(Base):
    __tablename__   = "addresses"
    id              = Column(mysql.BIGINT, primary_key=True)
    address         = Column(mysql.CHAR(36))
    first_time      = Column(mysql.BIGINT)
    last_time       = Column(mysql.BIGINT)
    num_txns        = Column(mysql.BIGINT)
    total_received  = Column(mysql.BIGINT)
    final_balance   = Column(mysql.BIGINT)
