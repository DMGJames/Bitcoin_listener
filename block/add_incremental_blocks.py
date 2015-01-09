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
from sqlalchemy import and_
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
import signal
from common import SignalSystemExit, set_session, get_hostname_or_die
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

class BlockchainUpdater:
    def __init__(self, session, rpc_url):
        self.session = session
        self.bitcoin_client = BitcoinClient(rpc_url=rpc_url)
    
        self.caught_term_signal = False
        self.__register_signals__()

        self.block_id = 1
        self.tx_id = 1
        self.input_id = 1
        self.output_id = 1

        self.is_dotting = False
    
    def __register_signals__(self):
        uncatchable = ['SIG_DFL','SIGSTOP','SIGKILL']
        for i in [x for x in dir(signal) if x.startswith("SIG")]:
            if not i in uncatchable:
                signum = getattr(signal,i)
                signal.signal(signum, self.__receive_signal__)
                
    def __receive_signal__(self, signum, stack):
        if signum in [1,2,3,15]:
            if self.is_dotting is True:
                stdout.write(" Interrupted by signal %s\n" % str(signum))
            else:
                print 'Interrupted by signal %s' % str(signum)
            self.is_dotting = False
            raise SignalSystemExit()
        else:
            pass

    def run(self):
        tip = self.__get_blockchain_tip__()
        if tip is None:
            print "Blockchain does not exist"
            tip = self.__initialize_genesis_block__()
            height = 0
            hash = tip[ATTRIBUTE_HASH]
        else:
            height = tip.height
            hash = tip.hash

        print "Blockchain tip {}:{}".format(height, hash)
        updated_blocks = self.bitcoin_client.getblocksince(hash)
        self.__process_updated_blocks__(blocks=updated_blocks)

    def __get_blockchain_tip__(self):
        tip = self.session.query(BtcBlock).\
            filter(BtcBlock.is_active == True).\
            order_by(desc(BtcBlock.height)).\
            first()
        return tip

    def __initialize_genesis_block__(self):
        hash = self.bitcoin_client.getblockhash(0)
        block = self.bitcoin_client.getblock(hash)
        self.__process_active_block__(block)
        print "Initialized genesis block {}:{}".format(0, hash)
        return block

    def __process_updated_blocks__(self, blocks):
        active_blocks = blocks[ATTRIBUTE_ADDED]
        orphaned_blocks = blocks[ATTRIBUTE_REMOVED]
        self.__process_orphaned_blocks__(blocks=orphaned_blocks)
        self.__process_active_blocks__(blocks=active_blocks)
        
    def __process_orphaned_blocks__(self, blocks):
        print "Processing orphaned blocks...", len(blocks)
        for block in blocks:
            try:
                self.__process_orphaned_block__(block)
            except:
                self.__print_block_rollbacked__(block)
                raise

    def __process_orphaned_block__(self, block):
        height = block.get(ATTRIBUTE_HEIGHT)
        hash = block.get(ATTRIBUTE_HASH)
        print "Processing orphaned block {}:{}...".format(height, hash)

        query = self.session.query(BtcBlock)
        query.filter(and_(
            BtcBlock.height == height,
            BtcBlock.hash == hash))

        if query.all() is None:
            raise AssertionError("orphaned block not found")
        if len(query.all()) != 1:
            raise AssertionError("orphaned block not unique")
        block = query.first()
        if block.is_active is False:
            raise AssertionError("block already orphaned")

        block.is_active = False
        self.__commit__()

    def __process_active_blocks__(self, blocks):
        print "Processing active blocks:", len(blocks)
        self.__prepare_ids__()
        for block in blocks:
            try:
                self.__process_active_block__(block)
            except:
                self.__print_block_rollbacked__(block)
                raise

    def __prepare_ids__(self):
        max_block_id = self.session.query(func.max(BtcBlock.id)).first()
        if max_block_id[0] is not None:
            self.block_id = max_block_id[0] + 1

        max_tx_id = self.session.query(func.max(BtcTransaction.id)).first()
        if max_tx_id[0] is not None:
            self.tx_id = max_tx_id[0] + 1

        max_input_id = self.session.query(func.max(BtcInput.id)).first()
        if max_input_id[0] is not None:
            self.input_id = max_input_id[0] + 1

        max_output_id = self.session.query(func.max(BtcOutput.id)).first()
        if max_output_id[0] is not None:
            self.output_id = max_output_id[0] + 1

    def __process_active_block__(self, block):
        height = block.get(ATTRIBUTE_HEIGHT)
        hash = block.get(ATTRIBUTE_HASH)
        print "Processing active block {}:{}...".format(height, hash)

        btc_block = self.session.query(BtcBlock).\
            filter(BtcBlock.height == height).\
            filter(BtcBlock.hash == hash).\
            first()

        if btc_block is not None:
            if btc_block.is_active is True:
                raise AssertionError("block already active")
            else:
                btc_block.is_active = True
                self.__commit__()
                return

        items = []
        new_block = BtcBlock(
            id=self.block_id,
            height=height,
            is_active=True,
            hash=hash,
            time=block.get(ATTRIBUTE_TIME),
            pushed_from=get_hostname_or_die())
        items.append(new_block)

        txs = self.bitcoin_client.getblocktxs(hash)

        for tx in txs:
            self.__process_transaction__(tx, self.block_id, items)
        self.block_id += 1

        self.__add_items__(items)
        self.__commit__()

    def __process_transaction__(self, tx, block_id, items):
        hash = tx.get(ATTRIBUTE_TXID)
        is_coinbase = self.__is_coinbase__(tx)

        new_transaction = BtcTransaction(
            id=self.tx_id,
            block_id=block_id,
            hash=hash,
            is_coinbase=is_coinbase)
        items.append(new_transaction)

        vin = tx.get(ATTRIBUTE_VIN)
        for offset, vin_data in enumerate(vin):
            self.__process_txin__(vin_data, self.tx_id, is_coinbase, offset, items)

        vout = tx.get(ATTRIBUTE_VOUT)
        for offset, vout_data in enumerate(vout):
            self.__process_txout__(vout_data, self.tx_id, offset, items)

        self.tx_id += 1

    def __process_txin__(self, txin, tx_id, is_coinbase, offset, items):
        if is_coinbase:
            script_sig = txin.get(ATTRIBUTE_COINBASE)
            output_hash = "\0" * 32
            output_n = -1
        else:
            script_sig = txin.get(ATTRIBUTE_SCRIPT_SIG) \
                             .get(ATTRIBUTE_HEX)
            output_hash = txin.get(ATTRIBUTE_TXID)
            output_n = txin.get(ATTRIBUTE_VOUT)

        if len(script_sig) > 500:
            script_sig = None

        new_input = BtcInput(
            id=self.input_id,
            tx_id=tx_id,
            output_hash=output_hash,
            output_n=output_n,
            script_sig=script_sig,
            offset=offset)

        items.append(new_input)
        self.input_id += 1

    def __process_txout__(self, txout, tx_id, offset, items):
        script_pubkey = txout.get(ATTRIBUTE_SCRIPT_PUB_KEY)
        if script_pubkey is None:
            raise AssertionError("scriptPubKey does not exist")

        addresses = script_pubkey.get(ATTRIBUTE_ADDRESSES)
        if addresses is None: return

        for address in addresses:
            new_output = BtcOutput(
                id=self.output_id,
                tx_id=tx_id,
                dst_address=address,
                value=(int)(txout.get(ATTRIBUTE_VALUE)*100000000),
                offset=offset)
            items.append(new_output)
            self.output_id += 1

    def __add_items__(self, items):
        statistics = self.__get_statistics__(items)
        stdout.write("Adding %d items" % len(items))
        self.is_dotting = True
        for item in items:
            stdout.write(".")
            stdout.flush()
            self.session.add(item)
        stdout.write(" Done\n")
        self.is_dotting = False
        print "  " \
              "%(block)i blocks, " \
              "%(tx)i transactions, " \
              "%(txin)i inputs, " \
              "%(txout)i outputs" % statistics

    def __commit__(self):
        stdout.write("Committing...")
        self.is_dotting = True
        self.session.commit()
        stdout.write(" Done\n")
        self.is_dotting = False

    def __print_block_rollbacked__(self, block):
        if self.is_dotting is True: stdout.write(" Failed\n")
        height = block.get(ATTRIBUTE_HEIGHT)
        hash = block.get(ATTRIBUTE_HASH)
        print "Rolled back block {}:{}".format(height, hash)

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
                raise AssertionError("unknown item type")

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
    print "Environment:", env_setting
    if is_process_running():
        print "Process is already running. Skip this round"
        sys.exit()

    try:
        make_lock_file()
    except IOError as e:
        sys.exit("Can't open lock file")
    except:
        raise

    try:
        session = set_session(env_setting=env_setting)
        updater = BlockchainUpdater(
            session=session,
            rpc_url=DEFAULT_LOCAL_BITCONID_RPC_URL)
        updater.run()
        remove_lock_file()
        print "Program completed successfully"
    except SignalSystemExit as e:
        remove_lock_file()
        print "Program terminated normally"
        sys.exit()
    except:
        remove_lock_file()
        raise
