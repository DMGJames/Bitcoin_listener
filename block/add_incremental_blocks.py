#!/usr/bin/env python
'''
Created on Jul 21, 2014

@author: yutelin
'''
##### Set environment #####

import os
from os.path import sys
from sys import stdout

def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir+"/../")

set_env()
############################
from sqlalchemy.sql.functions import func
import signal
from common import set_session, get_hostname_or_die
from bitcoin_client import BitcoinClient
from constants import DEFAULT_LOCAL_BITCONID_RPC_URL, ATTRIBUTE_ADDED,\
    ATTRIBUTE_REMOVED, ATTRIBUTE_HEIGHT, ATTRIBUTE_HASH, ATTRIBUTE_TIMESTAMP,\
    ATTRIBUTE_VIN, ATTRIBUTE_VOUT, ATTRIBUTE_COINBASE, ATTRIBUTE_TXID,\
    ATTRIBUTE_SCRIPT_PUB_KEY, ATTRIBUTE_ADDRESSES, ATTRIBUTE_VALUE
from models import BtcBlock, BtcTransaction, BtcInput, BtcOutput


LOCK_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "add_incremental_blocks.lock") 
def is_process_running():
    print "Check lock file", LOCK_FILE
    return os.path.exists(LOCK_FILE)

def make_lock_file():
    with open(LOCK_FILE, 'a'):
        os.utime(LOCK_FILE, None)
   
def remove_lock_file():
    os.remove(LOCK_FILE)

class AddIncrementalBlocks:
    def __init__(self, query_session, update_session, rpc_url):
        self.query_session = query_session
        self.update_session = update_session
        self.bitcoin_client = BitcoinClient(rpc_url=rpc_url)
    
        self.caught_term_signal = False
        self.__register_signals__()
    
    def __register_signals__(self):
        uncatchable = ['SIG_DFL','SIGSTOP','SIGKILL']
        for i in [x for x in dir(signal) if x.startswith("SIG")]:
            if not i in uncatchable:
                signum = getattr(signal,i)
                signal.signal(signum,self.__receive_signal__)
                
    def __receive_signal__(self, signum, stack):
        if signum in [1,2,3,15]:
            print 'Caught signal %s, exiting.' %(str(signum))
            self.caught_term_signal = True
        else:
            print 'Caught signal %s, ignoring.' %(str(signum))

    def __check_term_signal__(self):
        if(self.caught_term_signal):
            print "Got term signal. Exit."
            sys.exit()
        
    def add_incremental_blocks(self):
        #1. Get latest block hash
        block_hash = self.__get_latest_block_hash__()
        print "Latest block hash:", block_hash
        
        #2. Process new blocks by calling RPC call getblocksince
        if block_hash:
            new_blocks = self.bitcoin_client.getblocksince(block_hash)
            #print new_blocks
            self.__process_new_blocks__(blocks = new_blocks)
        else:
            print "Latest block hash is None. ERROR! exit!"
        
    def __get_latest_block_hash__(self):
        result = None
        latest_block_id = self.query_session.query(func.max(BtcBlock.id)).first()
        if latest_block_id:
            latest_block = self.query_session.query(BtcBlock).filter(BtcBlock.id == latest_block_id[0]).first()
            if latest_block: result = latest_block.hash 
        return result
    
    def __process_new_blocks__(self, blocks):
        added_blocks = blocks[ATTRIBUTE_ADDED]
        removed_blocks = blocks[ATTRIBUTE_REMOVED]
        print "Process removed blocks: ", len(removed_blocks)
        self.__process_removed_blocks__(removed_blocks = removed_blocks)
        
        print "Process added blocks: ", len(added_blocks)
        self.__process_added_blocks__(added_blocks = added_blocks)
        
    def __process_removed_blocks__(self, removed_blocks):
        if not removed_blocks or len(removed_blocks) == 0: return
        
        #1. Get min block id
        block_ids = [int(block.get(ATTRIBUTE_HEIGHT)) for block in removed_blocks]
        min_block_id = min(block_ids)
        
        #2. Get min TxId
        min_tx = min_input = min_output = None
        min_tx_id = self.query_session.query(func.min(BtcTransaction.id)).filter(BtcTransaction.blockID == min_block_id).first()
        
        if min_tx_id:
            min_tx_id = min_tx_id[0]
            min_tx = self.query_session.query(BtcTransaction).filter(BtcTransaction.id == min_tx_id).first()
    
        #print "min_tx:", min_tx.hash
        #3. Get min inputId
        if min_tx:
            min_input = self.query_session.query(BtcInput).filter(BtcInput.txHash == min_tx.hash).first()
            
        #4. Get min outputId
        if min_tx:
            min_output = self.query_session.query(BtcOutput).filter(BtcOutput.txHash == min_tx.hash).first()
        
        #5. Delete blocks
        # print "min_block_id:", min_block_id
        self.update_session.query(BtcBlock).filter(BtcBlock.id >= min_block_id).delete()
        
        #6. Delete transactions
        self.update_session.query(BtcTransaction.blockID >= min_block_id).delete()
        # print "min_block_id:", min_block_id
        
        #7. Delete inputs
        if min_input:
            self.update_session.query(BtcInput.id >= min_input.id).delete()
        #print "min_input", min_input.id
        
        #8. Delete outputs
        if min_output:
            self.update_session.query(BtcOutput.id >= min_output.id).delete()
        #print "min_output", min_output.id
        #9. Commit changes
        try:
            self.__check_term_signal__()
            self.update_session.commit()
            self.__check_term_signal__()
        except Exception, e:
            print "Exception on __process_removed_blocks__:", e
            self.update_session.rollback()
        finally:
            self.update_session.close()
                
    def __process_added_blocks__(self, added_blocks):
        if not added_blocks or len(added_blocks) == 0: return
        
        #1. Sort array
        added_blocks = sorted(added_blocks, key=lambda k: k[ATTRIBUTE_HEIGHT])
        
        #2. Get max input/output id
        tx_id = input_id = output_id = 1
        max_tx_id = self.query_session.query(func.max(BtcTransaction.id)).first()
        if max_tx_id[0]: tx_id = max_tx_id[0]+1
        max_input_id = self.query_session.query(func.max(BtcInput.id)).first()
        if max_input_id[0]: input_id = max_input_id[0]+1
        max_output_id = self.query_session.query(func.max(BtcOutput.id)).first()
        if max_output_id[0]: output_id = max_output_id[0]+1
        
        #2. Iterate through blocks
        for block in added_blocks:
            new_items = []
            #1. Add block
            new_block = BtcBlock(id=block.get(ATTRIBUTE_HEIGHT),
                                 hash=block.get(ATTRIBUTE_HASH),
                                 time=block.get(ATTRIBUTE_TIMESTAMP),
                                 pushed_from=get_hostname_or_die())
            new_items.append(new_block)
            print new_block.__dict__
            
            #2. Get transactions from the block
            txs = self.bitcoin_client.getblocktxs(block.get(ATTRIBUTE_HASH))
            
            #3. Iterate through txs
            for tx in txs:
                #3.1 Process transaction
                hash = tx.get(ATTRIBUTE_TXID)
                is_coinbase = self.__is_coinbase__(tx)
                new_transaction = BtcTransaction(
                    id=tx_id,
                    hash=hash,
                    blockID=block.get(ATTRIBUTE_HEIGHT),
                    is_coinbase=is_coinbase,
                    pushed_from=get_hostname_or_die()
                )
                tx_id += 1
#                 print new_transaction.__dict__
                new_items.append(new_transaction) 
                
                #3.2 Process VIN
                vin = tx.get(ATTRIBUTE_VIN)
                for offset, vin_data in enumerate(vin):
                    if(vin_data.get(ATTRIBUTE_COINBASE)):
                        new_input = BtcInput(id=input_id,
                                             txHash=tx.get(ATTRIBUTE_TXID),
                                             outputHash='0000000000000000000000000000000000000000000000000000000000000000',
                                             outputN=-1,
                                             offset=offset,
                                             pushed_from=get_hostname_or_die())
                    else:
                        new_input = BtcInput(id=input_id,
                                             txHash=tx.get(ATTRIBUTE_TXID),
                                             outputHash=vin_data.get(ATTRIBUTE_TXID),
                                             outputN=vin_data.get(ATTRIBUTE_VOUT),
                                             offset=offset,
                                             pushed_from=get_hostname_or_die())
                    input_id += 1
#                         print new_input.__dict__
                    new_items.append(new_input)
                     
                #3.3 Process VOUT
                vout = tx.get(ATTRIBUTE_VOUT)
                for offset, vout_data in enumerate(vout):
                    # here we use 'X' to be consistent with previous implementations, because our table does not support multisig not using P2sh
                    address = 'X'
                    if vout_data.get(ATTRIBUTE_SCRIPT_PUB_KEY) and vout_data.get(ATTRIBUTE_SCRIPT_PUB_KEY).get(ATTRIBUTE_ADDRESSES) and \
                        len(vout_data.get(ATTRIBUTE_SCRIPT_PUB_KEY).get(ATTRIBUTE_ADDRESSES)) == 1:
                        address = vout_data.get(ATTRIBUTE_SCRIPT_PUB_KEY).get(ATTRIBUTE_ADDRESSES)[0]
                    new_output = BtcOutput(id=output_id,
                                           dstAddress=address,
                                           value=(int)(vout_data.get(ATTRIBUTE_VALUE)*100000000),
                                           txHash=tx.get(ATTRIBUTE_TXID),
                                           offset=offset,
                                           pushed_from=get_hostname_or_die())
                    output_id += 1
#                     print new_output.__dict__
                    new_items.append(new_output)
                
            #4. Commit changes
            try:
                self.__check_term_signal__()
                print "Add:", len(new_items)
                for item in new_items:
                    self.__check_term_signal__()
                    stdout.write(".")
                    stdout.flush()
#                     print item.__dict__
                    self.update_session.add(item)
#                     print item.__class__.__name__, ":", item.id
                print "" 
                new_items = []
                self.__check_term_signal__()
                print "Adding...."
                self.update_session.commit()
                print "Added"
                self.__check_term_signal__()
            except Exception, e:
                print "Exception on __process_added_blocks__:", e
                self.update_session.rollback()
                return 
            finally:
                self.update_session.close()
            print "Finish adding block: ", block.get(ATTRIBUTE_HEIGHT), "----------------------------------------------------------------------------"

    def __is_coinbase__(self, tx):
        vin = tx.get(ATTRIBUTE_VIN)
        return vin[0].get(ATTRIBUTE_COINBASE) is not None

env_setting = 'local'
if __name__ == '__main__':
    env_setting = sys.argv[1]
    print "Start: ---------------------------------------------------------------------------------"
    print "Environment:" , env_setting
    if is_process_running():
        print "Process is already running, skip this round"
    else:        
        make_lock_file()
        query_session = set_session(env_setting=env_setting)
        update_session = set_session(env_setting=env_setting)
        adder = AddIncrementalBlocks(query_session=query_session, update_session = update_session, rpc_url = DEFAULT_LOCAL_BITCONID_RPC_URL)
        adder.add_incremental_blocks()
        remove_lock_file()
    print "Done!"
    print "End: -----------------------------------------------------------------------------------"
