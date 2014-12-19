#!/usr/bin/env python
'''
Created on Jul 21, 2014

@author: yutelin
'''
##### Set environment #####

import os
from os.path import sys
from sys import stdout, stderr

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
from constants import DEFAULT_LOCAL_BITCONID_RPC_URL, ATTRIBUTE_ADDED, \
    ATTRIBUTE_REMOVED, ATTRIBUTE_HEIGHT, ATTRIBUTE_HASH, ATTRIBUTE_TIME, \
    ATTRIBUTE_VIN, ATTRIBUTE_VOUT, ATTRIBUTE_COINBASE, ATTRIBUTE_TXID, \
    ATTRIBUTE_SCRIPT_PUB_KEY, ATTRIBUTE_ADDRESSES, ATTRIBUTE_VALUE, \
    ATTRIBUTE_SCRIPT_SIG, ATTRIBUTE_HEX
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

        self.tx_id = 1
        self.input_id = 1
        self.output_id = 1
    
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
        if block_hash is None:
            print "No block found"
            block_hash = self.__add_genesis_block__()
        else:
            print "Latest block hash:", block_hash
        
        #2. Process new blocks by calling RPC call getblocksince
        new_blocks = self.bitcoin_client.getblocksince(block_hash)
        self.__process_new_blocks__(blocks = new_blocks)

    def __get_latest_block_hash__(self):
        result = None
        latest_block_id = self.query_session.query(func.max(BtcBlock.id)).first()
        if latest_block_id:
            latest_block = self.query_session.query(BtcBlock).filter(BtcBlock.id == latest_block_id[0]).first()
            if latest_block: result = latest_block.hash 
        return result

    def __add_genesis_block__(self):
        genesis_hash = self.bitcoin_client.getblockhash(0)
        genesis_block = self.bitcoin_client.getblock(genesis_hash)
        self.__process_added_block__(genesis_block)
        return genesis_hash

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
        except (SystemExit, Exception) as e:
            print "Exception on __process_removed_blocks__:", e
            self.update_session.rollback()
        finally:
            self.update_session.close()
                
    def __process_added_blocks__(self, added_blocks):
        if not added_blocks or len(added_blocks) == 0: return
        
        #1. Sort array
        added_blocks = sorted(added_blocks, key=lambda k: k[ATTRIBUTE_HEIGHT])
        
        #2. Get max input/output id
        max_tx_id = self.query_session.query(func.max(BtcTransaction.id)).first()
        if max_tx_id[0]: self.tx_id = max_tx_id[0]+1
        max_input_id = self.query_session.query(func.max(BtcInput.id)).first()
        if max_input_id[0]: self.input_id = max_input_id[0]+1
        max_output_id = self.query_session.query(func.max(BtcOutput.id)).first()
        if max_output_id[0]: self.output_id = max_output_id[0]+1
        
        #2. Iterate through blocks
        for block in added_blocks:
            self.__process_added_block__(block)

    def __process_added_block__(self, block):
        items = []
        #1. Add block
        height = block.get(ATTRIBUTE_HEIGHT)
        hash = block.get(ATTRIBUTE_HASH)

        print "Processing block {}:{}...".format(height, hash)
        new_block = BtcBlock(
            id=height,
            hash=hash,
            time=block.get(ATTRIBUTE_TIME),
            pushed_from=get_hostname_or_die())
        items.append(new_block)

        #2. Get transactions from the block
        txs = self.bitcoin_client.getblocktxs(hash)

        #3. Iterate through txs
        for tx in txs:
            self.__process_transaction__(tx, height, items)

        #4. Commit changes
        self.__commit_items__(items)

    def __process_transaction__(self, tx, block_id, items):
        #3.1 Process transaction
        hash = tx.get(ATTRIBUTE_TXID)
        is_coinbase = self.__is_coinbase__(tx)

        new_transaction = BtcTransaction(
            id=self.tx_id,
            hash=hash,
            blockID=block_id,
            is_coinbase=is_coinbase,
            pushed_from=get_hostname_or_die())
        self.tx_id += 1
        items.append(new_transaction)

        #3.2 Process VIN
        vin = tx.get(ATTRIBUTE_VIN)
        for offset, vin_data in enumerate(vin):
            self.__process_txin__(vin_data, tx, offset, items)

        #3.3 Process VOUT
        vout = tx.get(ATTRIBUTE_VOUT)
        for offset, vout_data in enumerate(vout):
            self.__process_txout__(vout_data, tx, offset, items)

    def __process_txin__(self, txin, tx, offset, items):
        if self.__is_coinbase__(tx):
            script_sig = txin.get(ATTRIBUTE_COINBASE)
            outputHash = "\0" * 32
            outputN = -1
        else:
            script_sig = txin.get(ATTRIBUTE_SCRIPT_SIG) \
                             .get(ATTRIBUTE_HEX)
            outputHash = txin.get(ATTRIBUTE_TXID)
            outputN = txin.get(ATTRIBUTE_VOUT)

        new_input = BtcInput(
            id=self.input_id,
            txHash=tx.get(ATTRIBUTE_TXID),
            outputHash=outputHash,
            outputN=outputN,
            script_sig=script_sig,
            offset=offset,
            pushed_from=get_hostname_or_die())

        self.input_id += 1
        items.append(new_input)

    def __process_txout__(self, txout, tx, offset, items):
        # here we use 'X' to be consistent with previous implementations,
        # because our table does not support multisig not using P2sh
        address = 'X'
        script_pubkey = txout.get(ATTRIBUTE_SCRIPT_PUB_KEY)
        addresses = script_pubkey.get(ATTRIBUTE_ADDRESSES)
        if script_pubkey and addresses and len(addresses) == 1:
            address = addresses[0]

        new_output = BtcOutput(
            id=self.output_id,
            dstAddress=address,
            value=(int)(txout.get(ATTRIBUTE_VALUE)*100000000),
            txHash=tx.get(ATTRIBUTE_TXID),
            offset=offset,
            pushed_from=get_hostname_or_die())

        self.output_id += 1
        items.append(new_output)

    def __commit_items__(self, items):
        try:
            self.__check_term_signal__()
            statistics = self.__get_statistics__(items)
            stdout.write("Adding %d items" % len(items))
            is_dotting = True
            for item in items:
                self.__check_term_signal__()
                stdout.write(".")
                stdout.flush()
                self.update_session.add(item)
            stdout.write(" Done\n")
            is_dotting = False
            print "  " \
                  "%(block)i blocks, " \
                  "%(tx)i transactions, " \
                  "%(txin)i inputs, " \
                  "%(txout)i outputs" % statistics

            new_items = []
            self.__check_term_signal__()
            stdout.write("Committing...")
            is_dotting = True
            self.update_session.commit()
            stdout.write(" Done\n")
            is_dotting = False
            self.__check_term_signal__()
            return True
        except (SystemExit, Exception) as e:
            print >> stderr, "Exception:", e
            if is_dotting: stdout.write(" Failed\n")
            stdout.write("Rolling back...")
            self.update_session.rollback()
            stdout.write(" Done\n")
            return False
        finally:
            self.update_session.close()

    def __is_coinbase__(self, tx):
        vin = tx.get(ATTRIBUTE_VIN)
        return vin[0].get(ATTRIBUTE_COINBASE) is not None

    def __get_statistics__(self, items):
        num_blocks = num_txs = num_txins = num_txouts = 0
        for item in items:
            if isinstance(item, BtcBlock):
                num_blocks += 1
            elif isinstance(item, BtcTransaction):
                num_txs += 1
            elif isinstance(item, BtcInput):
                num_txins += 1
            elif isinstance(item, BtcOutput):
                num_txouts += 1
            else:
                raise "Unknown type"

        result = {
            "block": num_blocks,
            "tx": num_txs,
            "txin": num_txins,
            "txout": num_txouts
        }
        return result
        
env_setting = 'local'
if __name__ == '__main__':
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    if is_process_running():
        print "Process is already running, skip this round"
    else:        
        make_lock_file()
        query_session = set_session(env_setting=env_setting)
        update_session = set_session(env_setting=env_setting)
        adder = AddIncrementalBlocks(query_session=query_session, update_session = update_session, rpc_url = DEFAULT_LOCAL_BITCONID_RPC_URL)
        adder.add_incremental_blocks()
        print "Adding incremental blocks completed successfully"
        remove_lock_file()
