#!/usr/bin/env python
'''
Created on Jun 29, 2014

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
from common import set_session
from models import Transaction
import json
from constants import ATTRIBUTE_BLOCK_HEIGHT, ATTRIBUTE_TXID,\
    ATTRIBUTE_BLOCKHASH, ATTRIBUTE_HEIGHT, DEFAULT_BITCOIND_RPC_URL,\
    ATTRIBUTE_BLOCK_HASH
import httplib2
import threadpool
from bitcoinrpc.proxy import AuthServiceProxy

LOCK_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "transaction_post_process.lock") 
def is_process_running():
    print "Check lock file", LOCK_FILE
    return os.path.exists(LOCK_FILE)

def make_lock_file():
    with open(LOCK_FILE, 'a'):
        os.utime(LOCK_FILE, None)
   
def remove_lock_file():
    os.remove(LOCK_FILE)


class TransactionPostProcess():
    def __init__(self, query_session, update_session):
        self.query_session = query_session
        self.update_session = update_session
        self.pool_size = 20
        self.pool = threadpool.ThreadPool(self.pool_size)
        self.txs = []
        
    def __get_block_height_via_blockchain_info__(self, txid):
        h = httplib2.Http()
        url = "http://blockchain.info/rawtx/%s" %(txid)
        _, content = h.request(url, "GET")
        tx_dict = json.loads(content)
        result = tx_dict.get(ATTRIBUTE_BLOCK_HEIGHT)
        return result
    
    def __get_block_height_and_hash_via_rpc__(self, txid):
        result = (None,None)
        rpc_tx = blockhash = block = height = None
        try:
            access = AuthServiceProxy(DEFAULT_BITCOIND_RPC_URL)
            rpc_tx = access.getrawtransaction(txid, 1)
            blockhash = rpc_tx.get(ATTRIBUTE_BLOCKHASH)
            block = access.getblock(blockhash)
            height = block.get(ATTRIBUTE_HEIGHT)
            result =  (height, blockhash)
        except Exception, e:
            print "Exception on __get_block_height_and_hash_via_rpc__:", txid, e, rpc_tx, blockhash, block, height
        return result
    
    def __get_block_height_and_hash__(self, txid=None):
        result = (None,None)
        try:
            if txid:
                #result = self.__get_block_height_via_blockchain_info__(txid=txid)
                result = self.__get_block_height_and_hash_via_rpc__(txid=txid)
                print "block_height/hash:", result
        except Exception, e:
            print "Exception on __get_block_height_and_hash__:", txid, e
        return result    
    
    def __update_transaction__(self, transaction):
        (height, blockhash)= self.__get_block_height_and_hash__(transaction.get(ATTRIBUTE_TXID))
        transaction[ATTRIBUTE_BLOCK_HEIGHT] = height
        transaction[ATTRIBUTE_BLOCK_HASH] = blockhash 
        self.txs.append(transaction)    
        
    def __merge_transactions__(self, transactions):
        try:
            for tx in transactions:
                if tx.get(ATTRIBUTE_BLOCK_HEIGHT):
                    self.update_session.query(Transaction).filter(Transaction.txid == tx.get(ATTRIBUTE_TXID)).\
                        update({ATTRIBUTE_BLOCK_HEIGHT:tx.get(ATTRIBUTE_BLOCK_HEIGHT),
                                ATTRIBUTE_BLOCK_HASH:tx.get(ATTRIBUTE_BLOCK_HASH)})
            self.update_session.commit()
        except Exception,e:
            print "Exception on __merge_transactions__:", e   
        
    def run_post_process(self):
        print "run post process"
        #1. Get all transactions
        txs = self.query_session.query(Transaction).filter(Transaction.block_hash == None).all()
        for tx in txs:
            while self.pool._requests_queue.qsize() > len(self.pool.workers) :
                self.pool.wait()
                self.__merge_transactions__(self.txs)
                self.txs = []              
            requests = threadpool.makeRequests(self.__update_transaction__, [tx.__dict__])
            for req in requests: self.pool.putRequest(req)
        self.pool.wait()
        self.__merge_transactions__(self.txs)
        self.txs = []

if __name__ == '__main__':
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    if is_process_running():
        print "Process is already running, skip this round"
    else:        
        make_lock_file()
        query_session = set_session(env_setting=env_setting)
        update_session = set_session(env_setting=env_setting)
        post_process = TransactionPostProcess(query_session=query_session, update_session = update_session)
        post_process.run_post_process()
        remove_lock_file()
    print "Done!"