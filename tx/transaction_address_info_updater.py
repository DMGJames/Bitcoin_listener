#!/usr/bin/env python
'''
Created on Jul 8, 2014

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
############################
from common import set_session
from models import TransactionAddressInfoUpdate, TransactionOutput,\
    TransactionAddressInfo, TransactionInput
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.functions import func
import threading
from pprint import pprint

class TransactionAddressInfoUpdater:
    def __init__(self, update_session, query_session, start_height, end_height):
        self.update_session = update_session
        self.query_session = query_session
        self.start_height = start_height
        self.end_height = end_height
        self.query_lock = threading.Lock()
        
        if not self.start_height:
            self.start_height = self.__get_last_update__() + 1
            
        if not self.end_height:
            self.end_height = self.__get_max_pushed_block_height__()

        
    ## Get last TransactionAddressInfoUpdater object
    def __get_last_update__(self):
        result = 0
        self.query_lock.acquire(True)
        try:
            update_obj = self.query_session.query(TransactionAddressInfoUpdate).\
                order_by(desc(TransactionAddressInfoUpdate.updated_at)).first()
            result = 0 if update_obj == None else update_obj.block_height
            self.query_session.close()
        except Exception,e:
            print "Exception on __get_last_update__", e
        self.query_lock.release()
        return result
    
    ## Get max block height that has been stored in TransactionOutput table
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

    def start(self):
        print "Start, End: ", self.start_height, self.end_height
        while self.start_height <= self.end_height:
            current_height = self.start_height
            self.start_height += 1
            print "Handling:", current_height
            #1. Process outputs
            self.__process_transaction_output_at_height__(block_height = current_height)
            #2. Process inputs 
            self.__process_transaction_input_at_height__(block_height = current_height)
            #3. Update transaction address update
            self.__finish_update_at_height__(block_height = current_height)
        print "start"

    def __process_transaction_output_at_height__(self, block_height):
        print "Process output at:", block_height
        #1. Load all outputs at the same height
        txn_vouts = self.query_session.query(TransactionOutput).filter(TransactionOutput.block_height == block_height).all()
        all_addresses = [txn_vout.address for txn_vout in txn_vouts]
        self.query_session.close()
        print all_addresses
        
        #2. Load all address info to map, if doesn't exist, create a new one
        address_info_dict = self.__load_address_info_map__(all_addresses = all_addresses)
        for _, address_info in address_info_dict.iteritems():
            print address_info.__dict__
        
        #3. Add values from txn_vouts
        for txn_vout in txn_vouts:
            #1. Get associated address_info
            address_info = address_info_dict[txn_vout.address]
            #2. Add values
            address_info.vout_count += 1
            address_info.received_value += txn_vout.value
            address_info.balance += txn_vout.value
            if txn_vout.is_from_coinbase: address_info.coinbase += 1 
        print "After adding values"
        for _, address_info in address_info_dict.iteritems():
            print address_info.__dict__
            
        #4. Update db
        for _, address_info in address_info_dict.iteritems():
            self.update_session.merge(address_info)
        try:
            self.update_session.commit()
            self.update_session.close()
        except Exception,e:
            print "Exception on __process_transaction_output_at_height__:", e
            self.update_session.rollback()
            self.update_session.close()
        
    def __process_transaction_input_at_height__(self, block_height):
        print "Process input at:", block_height
        #1. Load all inputs at the same height
        txn_vins = self.query_session.query(TransactionInput).\
            filter(TransactionInput.block_height == block_height, 
                   TransactionInput.vout_offset >= 0).all()
        self.query_session.close()
        print "All txn_vins:", txn_vins
        #2. Get all address
        all_addresses = []
        txn_vin_vout_dict = {}
        key_format = "%s------%i"
        for txn_vin in txn_vins:
            txn_vout = self.query_session.query(TransactionOutput).filter(TransactionOutput.txid == txn_vin.output_txid, TransactionOutput.offset == txn_vin.vout_offset).first()
            print txn_vin.__dict__
            print txn_vout
            if txn_vout: 
                all_addresses.append(txn_vout.address)
                txn_vin_key = key_format % (txn_vin.output_txid, txn_vin.vout_offset)
                txn_vin_vout_dict[txn_vin_key] = txn_vout
            self.query_session.close() 
        print all_addresses
        print txn_vin_vout_dict
        
        #3. Load all address info to map, if doesn't exist, create a new one
        address_info_dict = self.__load_address_info_map__(all_addresses = all_addresses)
        for _, address_info in address_info_dict.iteritems():
            print address_info.__dict__
        
        #4. Subtract values from txn_vins
        for txn_vin in txn_vins:
            #1. Get associated address_info
            txn_vin_key = key_format % (txn_vin.output_txid, txn_vin.vout_offset)
            txn_vout = txn_vin_vout_dict.get(txn_vin_key)
            if txn_vout:
                address_info = address_info_dict.get(txn_vout.address)
                #2. Subtract values
                address_info.vin_count += 1
                address_info.spent_value += txn_vout.value
                address_info.balance -= txn_vout.value
        print "After subtracting values"
        for _, address_info in address_info_dict.iteritems():
            print address_info.__dict__
         
        #5. Update db
        for _, address_info in address_info_dict.iteritems():
            self.update_session.merge(address_info)
        try:
            self.update_session.commit()
            self.update_session.close()
        except Exception,e:
            print "Exception on __process_transaction_input_at_height__:", e
            self.update_session.rollback()
            self.update_session.close()
        
        
    def __finish_update_at_height__(self, block_height):
        update_obj = TransactionAddressInfoUpdate(block_height = block_height)
        self.update_session.merge(update_obj)
        try:
            self.update_session.commit()
        except Exception, e:
            print "Exception on __finish_update_at_height__", e
            self.update_session.rollback()
        
            
    def __load_address_info_map__(self, all_addresses):
        address_info_dict = {}
        address_infos = self.query_session.query(TransactionAddressInfo).filter(TransactionAddressInfo.address.in_(all_addresses)).all()
        for address_info in address_infos:
            address_info_dict[address_info.address] = address_info
        for address in all_addresses:
            if not address in address_info_dict:
                new_address_info = TransactionAddressInfo(address = address,
                                                          received_value = 0,
                                                          spent_value = 0,
                                                          balance = 0,
                                                          vin_count = 0,
                                                          vout_count = 0,
                                                          coinbase = 0)
                address_info_dict[address] = new_address_info
        return address_info_dict

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
    pusher = TransactionAddressInfoUpdater(update_session = update_session, 
                                      query_session =query_session,
                                      start_height=start,
                                      end_height=end)
    pusher.start()
    print "Done!"