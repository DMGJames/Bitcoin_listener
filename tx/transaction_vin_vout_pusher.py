#!/usr/bin/env python
'''
Created on Jul 3, 2014

@author: yutelin
'''

##### Set environment #####
import os
from os.path import sys
def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    #sys.path.append(file_dir)
    sys.path.append(file_dir+"/../")
    print sys.path
set_env()
########################################################################
from bitcoinrpc.proxy import AuthServiceProxy
from bitcoinrpc import proxy
from constants import ATTRIBUTE_BLOCK,\
    ATTRIBUTE_HASH, ATTRIBUTE_TXS, ATTRIBUTE_TXID, ATTRIBUTE_VOUT, ATTRIBUTE_N,\
    ATTRIBUTE_SCRIPT_PUB_KEY, ATTRIBUTE_ADDRESSES, ATTRIBUTE_VALUE,\
    ATTRIBUTE_VIN, ATTRIBUTE_TYPE, ATTRIBUTE_NULLDATA,\
    DEFAULT_LOADING_BATCH_SIZE, DEFAULT_SLEEP_TIME,\
    DEFAULT_MAI_REDIS_PASSWORD, DEFAULT_TX_ADDRESS_POOL_SIZE, ATTRIBUTE_HEIGHT,\
    DEFAULT_LOCAL_BITCONID_RPC_URL, ATTRIBUTE_COINBASE
from models import TransactionInput, TransactionOutput
from common import set_session
from sqlalchemy.sql.functions import func
from pusher import Pusher
import threading


class BlockLoader():
    def __init__(self, rpc_url):
        proxy.HTTP_TIMEOUT = 300
        self.rpc_access = AuthServiceProxy(rpc_url)
    
    def get_block(self, block_height):
        return self.rpc_access.getblockdetail(block_height)
    
    def get_block_aount(self):
        return self.rpc_access.getblockcount()
        
class TransactionVinVoutPusher(Pusher):        
    def __init__(self, update_session, query_session,rpc_url,
                 start_height=None, end_height=None,
                 batch_size = DEFAULT_LOADING_BATCH_SIZE,
                 sleep_time = DEFAULT_SLEEP_TIME,
                 password =  DEFAULT_MAI_REDIS_PASSWORD,
                 pool_size = DEFAULT_TX_ADDRESS_POOL_SIZE):
        super(TransactionVinVoutPusher, self).__init__(
                session = update_session,
                channel = None,
                queue = None,
                batch_size = batch_size,
                sleep_time = sleep_time,
                password = password,
                pool_size = pool_size)
        self.query_session = query_session
        self.start_height = start_height
        self.end_height = end_height
        self.block_loader = BlockLoader(rpc_url=rpc_url)
        self.query_lock = threading.Lock()
        self.load_lock = threading.Lock()
        
        if not self.start_height:
            #Note: this is only the guessing starting height since it is running multithreaded. 
            self.start_height = self.__get_max_pushed_block_height__()
        if not self.start_height:
            self.start_height = 1
        print "start:", self.start_height
        
        if not self.end_height:
            self.end_height = self.block_loader.get_block_aount()
        print "end:", self.end_height

    def listen(self):
        pass
    
    def load_data(self):
        self.load_lock.acquire(True)
        load_height = self.start_height
        self.start_height += 1
        self.load_lock.release()
        
        print "load data:",load_height
        result = []
        if not self.__check_block__(load_height):
            data = self.block_loader.get_block(load_height)
            result.append(data)
        return result

    ## Input: blocks
    def process_data(self, data):
        try:
            print "process data"
            result = []
            for block in data:
                #1. Read block info
                block_info = block.get(ATTRIBUTE_BLOCK)
                block_height = block_info.get(ATTRIBUTE_HEIGHT)
                block_hash = block_info.get(ATTRIBUTE_HASH) if block_info.get(ATTRIBUTE_HASH) else None
                print "block height, block hash:",block_height, block_hash 
                
                #2. Go deep into transactions
                txs = block.get(ATTRIBUTE_TXS)
                (tx_inputs, tx_outputs) = self.__txs_to_transaction_input_and_output_objects__(txs = txs, 
                    block_height = block_height, block_hash=block_hash)
                print "tx_inputs:tx_outputs:", len(tx_inputs), len(tx_outputs)
                result.extend(tx_inputs)
                result.extend(tx_outputs)

        except Exception, e:
            print "Error on process_data:", e
        return result

    def __check_block__(self, block_height):
        result = False
        self.query_lock.acquire(True)
        try:
            first_item = self.query_session.query(TransactionOutput).filter(TransactionOutput.block_height==block_height).first()
            result = first_item != None
#             count_rs = self.query_session.query(func.count(TransactionAddress)).filter(TransactionAddress.block_height==block_height).first()
#             for count in count_rs:
#                 result = (count[0] != 0)
            self.query_session.close()
        except Exception, e:
            self.query_session.rollback()
            print "Exception on __check_block__", e
        self.query_lock.release()
        return result
    
    def __get_max_pushed_block_height__(self):
        result = 1
        self.query_lock.acquire(True)
        try:
            count_rs = self.query_session.query(func.max(TransactionOutput.block_height))
            for count in count_rs:
                result = count[0] 
            self.query_session.close()
        except Exception, e:
            self.query_session.rollback()
            print "Exception on __get_max_pushed_block_height__", e
        self.query_lock.release()
        return result
    
    def __txs_to_transaction_input_and_output_objects__(self, txs, block_height, block_hash):
        tx_inputs = []
        tx_outputs = []
        if txs:
            for _, tx in enumerate(txs):
                txid = tx.get(ATTRIBUTE_TXID)
                is_from_coinbase = False
                #1. Get transaction inputs
                for offset, vin in enumerate(tx.get(ATTRIBUTE_VIN)):
                    output_txid = vin.get(ATTRIBUTE_TXID,"coinbase")
                    if vin.get(ATTRIBUTE_COINBASE): is_from_coinbase = True
                    vout_offset = vin.get(ATTRIBUTE_VOUT, -1)
                    tx_input = TransactionInput(txid = txid, 
                                                offset = offset,
                                                block_height = block_height,
                                                block_hash = block_hash,
                                                output_txid = output_txid, 
                                                vout_offset = vout_offset)
                    tx_inputs.append(tx_input)
                 
                #2. Get transaction outputs
                for vout in tx.get(ATTRIBUTE_VOUT):
                    value = vout.get(ATTRIBUTE_VALUE)
                    offset = vout.get(ATTRIBUTE_N)
                    script_pub_key = vout.get(ATTRIBUTE_SCRIPT_PUB_KEY)
                    address = None
                    if script_pub_key.get(ATTRIBUTE_TYPE) == ATTRIBUTE_NULLDATA:
                        address = ATTRIBUTE_NULLDATA
                        tx_output = TransactionOutput(txid = txid,
                                                       offset = offset,
                                                       address = address,
                                                       block_hash = block_hash,
                                                       block_height = block_height,
                                                       value = value,
                                                       is_from_coinbase = is_from_coinbase)
                        tx_outputs.append(tx_output)
                    else:
                        if vout.get(ATTRIBUTE_SCRIPT_PUB_KEY).get(ATTRIBUTE_ADDRESSES):
                            addresses = vout.get(ATTRIBUTE_SCRIPT_PUB_KEY).get(ATTRIBUTE_ADDRESSES)
                            for address in addresses:
                                tx_output = TransactionOutput(txid = txid,
                                                               offset = offset,
                                                               address = address,
                                                               block_hash = block_hash,
                                                               block_height = block_height,
                                                               value = value,
                                                               is_from_coinbase = is_from_coinbase)
                             
                                tx_outputs.append(tx_output)
        return (tx_inputs, tx_outputs)
    
    def __has_pending_data__(self):
        return self.start_height <= self.end_height
    
    def __print_loading_message__(self, loaded):
        print "Done loading transactions"

    def __print_pushing_message__(self,  pushed):
        print "Done pushing transactions:"
        for p in pushed:
            print '\t',
            p.print_pushing_message()
      
        
env_setting = 'local'
if __name__ == '__main__':
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    ## Single Thread
    start = None#120453 #159638 #150000
    end = None#150000#250000#71406#100000
    ### Pusher
    query_session = set_session(env_setting=env_setting)
    update_session = set_session(env_setting=env_setting)
    pusher = TransactionVinVoutPusher(update_session = update_session, 
                                      query_session =query_session,
                                      rpc_url = DEFAULT_LOCAL_BITCONID_RPC_URL,
                                      start_height=start,
                                      end_height=end)
    pusher.start()
    print "Done!"