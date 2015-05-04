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
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir + "/../")

set_env()

import signal
from common import SignalSystemExit, set_session, get_epoch_time
from constants import DEFAULT_LOCAL_BITCONID_RPC_URL
from bitcoin_client_wrapper import BitcoinClientWrapper
from bitcoin_client_wrapper import NextBlockHashNotReady
from models import Block as MBlock
from models import Transaction as MTransaction
from models import Input as MInput
from models import Output as MOutput
from models import Address as MAddress
from models import OutputsAddress as MOutputsAddress
from bitcoin_core import TxnoutType
import binascii
from mainchain_session import MainchainSession


LOCK_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mainchain_update.lock")
def is_process_running():
    print "Check lock file", LOCK_FILE
    return os.path.exists(LOCK_FILE)

def make_lock_file():
    with open(LOCK_FILE, 'a'):
        os.utime(LOCK_FILE, None)

def remove_lock_file():
    os.remove(LOCK_FILE)


class ItemStats:
    def __init__(self):
        self.num_blocks = 0
        self.num_transactions = 0
        self.num_inputs = 0
        self.num_outputs = 0
        self.num_addresses = 0
        self.num_outputs_addresses = 0

    def total_num_items(self):
        return \
            self.num_blocks + \
            self.num_transactions + \
            self.num_inputs + \
            self.num_outputs + \
            self.num_addresses + \
            self.num_outputs_addresses

    def to_dict(self):
        return {
            "total": self.total_num_items(),
            "block": self.num_blocks,
            "transaction": self.num_transactions,
            "input": self.num_inputs,
            "output": self.num_outputs,
            "address": self.num_addresses,
            "outputs address": self.num_outputs_addresses}

class MainchainUpdater(object):
    def __init__(self, session, rpc_url):
        self.session = MainchainSession(session)
        self.bitcoin_client = BitcoinClientWrapper(rpc_url=rpc_url)

        self.caught_term_signal = False
        self.__register_signals__()

        self.current_tx_id = 1
        self.current_input_id = 1
        self.current_output_id = 1
        self.current_address_id = 1

        self.item_stats = ItemStats()
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

    def run(self, count):
        tip = self.session.select_tip()
        if tip is None:
            print "Main chain does not exist"
            hash = self.__insert_genesis_block__()
        else:
            hash = binascii.b2a_hex(tip.hsh)
            print "Main chain tip {}:{}".format(tip.id, hash)

        try:
            print "Fetching blocks..."
            stdout.flush()
            blocks = self.bitcoin_client.get_blocks_since(hash, count)
        except NextBlockHashNotReady:
            print "Next block hash is not ready. Skip this round"
            return

        if blocks:
            print "Fetched {} active and {} orphaned blocks". \
                format(len(blocks["active"]), len(blocks["orphaned"]))
        else:
            print "Main chain is up-to-date"
            return

        self.__updated_blocks__(blocks=blocks)
        print "Main chain updated successfully"

    def insert_blocks(self, count):
        tip = self.session.select_tip()
        if tip is not None:
            tip_id = tip.id
            for i in range(0, count):
                height = tip_id + i + 1
                hash = self.bitcoin_client.get_block_hash(height)
                block = self.bitcoin_client.get_block(hash)
                self.__insert_block__(block)
        else:
            self.__insert_genesis_block__()

    def delete_blocks(self, count):
        tip = self.session.select_tip()
        if tip is not None:
            tip_id = tip.id
            for i in range(0, count):
                height = tip_id - i
                if height < 0: break
                hash = self.bitcoin_client.get_block_hash(height)
                block = self.bitcoin_client.get_block(hash)
                self.__delete_block__(block)

    def __set_current_ids__(self):
        id = self.session.select_max_id("transactions")
        self.current_tx_id = id + 1 if id is not None else 1

        id = self.session.select_max_id("inputs")
        self.current_input_id = id + 1 if id is not None else 1

        id = self.session.select_max_id("outputs")
        self.current_output_id = id + 1 if id is not None else 1

        id = self.session.select_max_id("addresses")
        self.current_address_id = id + 1 if id is not None else 1

    def __insert_genesis_block__(self):
        hash = self.bitcoin_client.get_block_hash(0)
        print "Inserting genesis block {}:{}...".format(0, hash)
        block = self.bitcoin_client.get_block(hash)
        self.__insert_block__(block)
        return hash

    def __updated_blocks__(self, blocks):
        active = blocks["active"]
        orphaned = blocks["orphaned"]
        self.__delete_blocks__(blocks=orphaned)
        self.__insert_blocks__(blocks=active)

    def __insert_blocks__(self, blocks):
        for block in blocks:
            self.__insert_block__(block)

    def __insert_block__(self, block):
        self.__reset_item_stats__()
        self.__set_current_ids__()
        print "Inserting block {}:{}...".format(block.height, block.hash)
        stdout.flush()

        try:
            received_time = get_epoch_time()
            m_block = MBlock(
                id=block.height,
                hsh=binascii.a2b_hex(block.hash),
                time=block.time,
                received_time=received_time)
            self.session.add(m_block)
            self.item_stats.num_blocks += 1

            self.__insert_transactions__(block, received_time)
            self.__commit__()
        except:
            self.__print_block_rollbacked__(block)
            raise
        finally:
            self.session.close()
            self.__reset_item_stats__()

    def __insert_transactions__(self, block, received_time):
        for tx in block.vtx:
            if self.__is_duplicate_transaction__(block.height, tx.hash):
                continue

            m_tx = MTransaction(
                id=self.current_tx_id,
                hsh=binascii.a2b_hex(tx.hash),
                block_id=block.height,
                received_time=received_time,
                fee=tx.get_fee(),
                total_out_value=tx.get_value_out(),
                num_inputs=len(tx.vin),
                num_outputs=len(tx.vout),
                coinbase=tx.is_coinbase(),
                lock_time=tx.lock_time)
            self.session.add(m_tx)
            self.item_stats.num_transactions += 1

            self.__insert_vin__(tx, self.current_tx_id)
            self.__insert_vout__(tx, self.current_tx_id, block.time)
            self.current_tx_id += 1

    def __insert_vin__(self, tx, tx_id):
        for offset, txin in enumerate(tx.vin):
            if tx.is_coinbase():
                output_id = -1
                type=255
                address_id = -2
                value = 0
            else:
                m_output = self.session.select_output(
                    hash=txin.prevout.hash,
                    offset=txin.prevout.n)
                assert m_output is not None
                m_output.spent = True

                output_id = m_output.id
                type = m_output.script_type
                address_id = m_output.address_id
                value = m_output.value

                if address_id > 0:
                    m_address = self.session.select_address(id=address_id)
                    assert m_address is not None
                    m_address.final_balance -= value
                    assert m_address.final_balance >= 0

            m_input = MInput(
                id=self.current_input_id,
                output_id=output_id,
                script_type=type,
                address_id=address_id,
                value=value,
                tx_id=tx_id,
                offset=offset)

            self.session.add(m_input)
            self.item_stats.num_inputs += 1
            self.current_input_id += 1

    def __insert_vout__(self, tx, tx_id, time):
        tx_addresses = set()

        for offset, txout in enumerate(tx.vout):
            address_counts = {}
            type = txout.script_pubkey.type

            if type == TxnoutType.TX_NONSTANDARD or \
               type == TxnoutType.TX_NULL_DATA:
                address_id = -1
            else:
                addresses = txout.script_pubkey.addresses
                assert type == TxnoutType.TX_MULTISIG or isinstance(addresses, list)

                if isinstance(addresses, list):
                    for address in addresses:
                        first_seen_in_tx = address not in tx_addresses
                        tx_addresses.add(address)

                        m_address = self.session.select_address(address=address)
                        if m_address is None:
                            m_address = MAddress(
                                id=self.current_address_id,
                                address=address,
                                first_time=time,
                                last_time=0,
                                num_txns=0,
                                total_received=0,
                                final_balance=0)

                            self.session.add(m_address)
                            self.item_stats.num_addresses += 1
                            self.current_address_id += 1

                        m_address.last_time = time,
                        if first_seen_in_tx is True:
                            m_address.num_txns += 1

                        if type == TxnoutType.TX_MULTISIG:
                            if m_address.id not in address_counts:
                                address_counts[m_address.id] = 1
                            else:
                                address_counts[m_address.id] += 1
                        else:
                            m_address.total_received += txout.value
                            m_address.final_balance += txout.value

                        address_id = m_address.id

                if type == TxnoutType.TX_MULTISIG:
                    address_id = -1

            for id, count in address_counts.iteritems():
                m_outputs_address = MOutputsAddress(
                    output_id=self.current_output_id,
                    address_id=id,
                    count=count)
                self.session.add(m_outputs_address)
                self.item_stats.num_outputs_addresses += 1

            m_output = MOutput(
                id=self.current_output_id,
                script_type=type.value,
                address_id=address_id,
                value=txout.value,
                tx_id=tx_id,
                offset=offset,
                spent=False)

            self.session.add(m_output)
            self.item_stats.num_outputs += 1
            self.current_output_id += 1

    def __delete_blocks__(self, blocks):
        for block in blocks:
            self.__delete_block__(block)

    def __delete_block__(self, block):
        self.__reset_item_stats__()
        print "Deleting block {}:{}...".format(block.height, block.hash)
        stdout.flush()

        try:
            m_block = self.session.select_block(id=block.height)
            assert m_block is not None

            self.__delete_inputs__(block.height)
            self.__delete_outputs__(block.height)
            self.__delete_transactions__(block.height)

            self.session.delete(m_block)
            self.item_stats.num_blocks += 1
            self.__commit__()
        except:
            self.__print_block_rollbacked__(block)
            raise
        finally:
            self.session.close()
            self.__reset_item_stats__()

    def __delete_transactions__(self, block_id):
        m_txes = self.session.select_transactions(block_id=block_id)
        assert m_txes

        for m_tx in m_txes:
            self.session.delete(m_tx)
            self.item_stats.num_transactions += 1

    def __delete_inputs__(self, block_id):
        m_inputs = self.session.select_inputs(block_id=block_id)
        assert m_inputs

        for m_input in m_inputs:
            if m_input.address_id > 0:
                m_prevout = self.session.select_output(id=m_input.output_id)
                assert m_prevout is not None
                m_address = self.session.select_address(id=m_input.address_id)
                assert m_address is not None
                m_address.final_balance += m_prevout.value

            self.session.delete(m_input)
            self.item_stats.num_inputs += 1

    def __delete_outputs__(self, block_id):
        tx_addresses = set()
        m_addresses_to_delete = []
        m_outputs = self.session.select_outputs(block_id=block_id)
        assert m_outputs

        for m_output in m_outputs:
            m_outputs_addresses_to_delete = []

            type = TxnoutType(m_output.script_type)
            if type == TxnoutType.TX_NONSTANDARD or \
               type == TxnoutType.TX_NULL_DATA:
                pass
            else:
                if type == TxnoutType.TX_MULTISIG:
                    m_outputs_addresses = self.session.select_outputs_addresses(
                        output_id=m_output.id)
                    assert m_outputs_addresses
                    address_ids = [a.address_id for a in m_outputs_addresses]

                    for m_output_address in m_outputs_addresses:
                        m_outputs_addresses_to_delete.append(m_output_address)
                else:
                    assert m_output.address_id > 0
                    address_ids = [m_output.address_id]

                for address_id in address_ids:
                    m_address = self.session.select_address(id=address_id)
                    assert m_address is not None
                    address = m_address.address

                    m_blocks = self.session.select_blocks(address=address)
                    assert m_blocks and m_blocks[-1].id == block_id

                    if len(m_blocks) > 1:
                        m_address.last_time = m_blocks[-2].time
                    else:
                        m_address.first_time = 0
                        m_address.last_time = 0

                    first_seen_in_tx = (m_output.tx_id, address) not in tx_addresses
                    if first_seen_in_tx is True:
                        m_address.num_txns -= 1
                        assert m_address.num_txns >= 0
                        tx_addresses.add((m_output.tx_id, address))

                    if type != TxnoutType.TX_MULTISIG:
                        m_address.total_received -= m_output.value
                        assert m_address.total_received >= 0
                        m_address.final_balance -= m_output.value
                        assert m_address.final_balance >= 0

                    if m_address.num_txns == 0:
                        m_addresses_to_delete.append(m_address)

            for a in m_outputs_addresses_to_delete:
                self.session.delete(a)
                self.item_stats.num_outputs_addresses += 1

            self.session.delete(m_output)
            self.item_stats.num_outputs += 1

        for a in m_addresses_to_delete:
            assert a.total_received == 0 and \
                   a.final_balance == 0
            self.session.delete(a)
            self.item_stats.num_addresses += 1

    def __print_item_stats__(self):
        print "Total %(total)i items with " \
              "%(block)i blocks, " \
              "%(transaction)i transactions, " \
              "%(input)i inputs, " \
              "%(output)i outputs, " \
              "%(address)i addresses, " \
              "%(outputs address)i outputs addresses" \
              % self.item_stats.to_dict()

    def __commit__(self):
        self.__print_item_stats__()
        stdout.write("Committing...")
        self.is_dotting = True
        self.session.commit()
        stdout.write(" Done\n")
        self.is_dotting = False

    def __print_block_rollbacked__(self, block):
        if self.is_dotting is True: stdout.write(" Failed\n")
        print "Rolled back block {}:{}".format(block.height, block.hash)

    def __is_duplicate_transaction__(self, height, txid):
        return \
            height == 91842 and txid == "d5d27987d2a3dfc724e359870c6644b40e497bdc0589a033220fe15429d88599" or \
            height == 91880 and txid == "e3bf3d07d4b0375638d5f1db5255fe07ba2c4cb067cd81b84ee974b6585fb468"

    def __reset_item_stats__(self):
        self.item_stats = ItemStats()

env_setting = 'local'
if __name__ == '__main__':

    try:
        env_setting = sys.argv[1]
        if env_setting not in ["local", "prod"]:
            raise ValueError

        if len(sys.argv) > 2:
            count = int(sys.argv[2])
        else:
            count = 1000
    except StandardError:
        print >> stderr, "wrong input arguments"
        print >> stderr, "usage: ./mainchain_update.py <local|prod> [count]"
        sys.exit(2)

    print "Set up environment to", env_setting
    if is_process_running():
        print "Process is already running. Skip this round"
        print "Program terminated normally"
        sys.exit()

    try:
        make_lock_file()
    except IOError as e:
        sys.exit("Can't open lock file")

    try:
        session = set_session(env_setting=env_setting)
        updater = MainchainUpdater(
            session=session,
            rpc_url=DEFAULT_LOCAL_BITCONID_RPC_URL)
        updater.run(count)
    except SignalSystemExit as e:
        pass
    finally:
        if os.path.exists(LOCK_FILE):
            remove_lock_file()

    print "Program terminated normally"
