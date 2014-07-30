'''
Created on Jun 19, 2014

@author: yutelin, webber
'''
from datetime import datetime
import json
from os.path import os, sys

from common import set_session
from constants import DEFAULT_MAI_REDIS_PASSWORD, DEFAULT_TX_QUEUE, DEFAULT_TX_CHANNEL, \
    ATTRIBUTE_TYPE, ATTRIBUTE_TXID, ATTRIBUTE_RELAYED_FROM, \
    ATTRIBUTE_RECEIVED_AT, ATTRIBUTE_TIME_RECEIVED, ATTRIBUTE_VALUE, ATTRIBUTE_VOUT, \
    DEFAULT_LOADING_BATCH_SIZE, DEFAULT_SLEEP_TIME, \
    ATTRIBUTE_SCRIPT_PUB_KEY, ATTRIBUTE_MULTISIG, ATTRIBUTE_NULLDATA, \
    ATTRIBUTE_PUBKEY, ATTRIBUTE_PUBKEYHASH, ATTRIBUTE_SCRIPTHASH, \
    ATTRIBUTE_HAS_MULTISIG, ATTRIBUTE_HAS_NULLDATA, ATTRIBUTE_HAS_PUBKEY, \
    ATTRIBUTE_HAS_SCRIPTHASH, ATTRIBUTE_HAS_PUBKEYHASH, DEFAULT_TXN_POOL_SIZE
from models import Transaction, TransactionInfo
from pusher import Pusher

class TransactionPusher(Pusher):
    def __init__(self, session,
                 channel = DEFAULT_TX_CHANNEL,
                 queue = DEFAULT_TX_QUEUE,
                 batch_size = DEFAULT_LOADING_BATCH_SIZE,
                 sleep_time = DEFAULT_SLEEP_TIME,
                 password =  DEFAULT_MAI_REDIS_PASSWORD,
                 pool_size = DEFAULT_TXN_POOL_SIZE):
        super(TransactionPusher, self).__init__(
            session = session,
            channel = channel,
            queue = queue,
            batch_size = batch_size,
            sleep_time = sleep_time,
            password = password,
            pool_size = pool_size)

    def process_data(self, data):
        try:
            json_txs = data
            result = []
            for json_tx in json_txs:
                dict_tx = self.__json_tx_to_dict_tx__(json_tx)
                tx = Transaction(txid = dict_tx.get(ATTRIBUTE_TXID),
                                 value = dict_tx.get(ATTRIBUTE_VALUE),
                                 has_multisig = dict_tx.get(ATTRIBUTE_HAS_MULTISIG),
                                 has_nulldata = dict_tx.get(ATTRIBUTE_HAS_NULLDATA),
                                 has_pubkey = dict_tx.get(ATTRIBUTE_HAS_PUBKEY),
                                 has_pubkeyhash = dict_tx.get(ATTRIBUTE_HAS_PUBKEYHASH),
                                 has_scripthash = dict_tx.get(ATTRIBUTE_HAS_SCRIPTHASH)
                                 )
                result.append(tx)
                tx_info = TransactionInfo(txid = dict_tx.get(ATTRIBUTE_TXID),
                                          relayed_from = dict_tx.get(ATTRIBUTE_RELAYED_FROM),
                                          received_at = dict_tx.get(ATTRIBUTE_RECEIVED_AT),
                                          json_string = json_tx)
                result.append(tx_info)
        except Exception, e:
            print "Error on process_data:", e
        return result

    def __json_tx_to_dict_tx__(self, json_tx):
        result = {}
        if json_tx:
            result = json.loads(json_tx)
            result[ATTRIBUTE_RECEIVED_AT] = datetime.strptime(result.get(ATTRIBUTE_TIME_RECEIVED), '%Y-%m-%d %H:%M:%S')
            result[ATTRIBUTE_VALUE] = 0
            has_multisig = has_nulldata = has_pubkey = has_pubkeyhash = has_scripthash = False
            for vout_item in result.get(ATTRIBUTE_VOUT):
                result[ATTRIBUTE_VALUE] = result[ATTRIBUTE_VALUE] + vout_item.get(ATTRIBUTE_VALUE)
                script_type = vout_item[ATTRIBUTE_SCRIPT_PUB_KEY][ATTRIBUTE_TYPE]
                if script_type == ATTRIBUTE_MULTISIG:
                    has_multisig = True
                elif script_type == ATTRIBUTE_NULLDATA:
                    has_nulldata = True
                elif script_type == ATTRIBUTE_PUBKEY:
                    has_pubkey = True
                elif script_type == ATTRIBUTE_PUBKEYHASH:
                    has_pubkeyhash = True
                elif script_type == ATTRIBUTE_SCRIPTHASH:
                    has_scripthash = True
            result[ATTRIBUTE_HAS_MULTISIG] = has_multisig
            result[ATTRIBUTE_HAS_NULLDATA] = has_nulldata
            result[ATTRIBUTE_HAS_PUBKEY] = has_pubkey
            result[ATTRIBUTE_HAS_PUBKEYHASH] = has_pubkeyhash
            result[ATTRIBUTE_HAS_SCRIPTHASH] = has_scripthash
        return result

    def __print_loading_message__(self, loaded):
        print "Done loading transactions"

    def __print_pushing_message__(self,  pushed):
        print "Done pushing transactions:"
        for p in pushed:
            print '\t',
            p.print_pushing_message()

def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)

if __name__ == '__main__':
    set_env()
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    session = set_session(env_setting=env_setting)
    pusher = TransactionPusher(session=session, batch_size=5, pool_size=200, sleep_time=10)
    pusher.start()
    
