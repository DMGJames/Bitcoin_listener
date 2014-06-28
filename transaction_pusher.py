'''
Created on Jun 19, 2014

@author: yutelin
'''
from os.path import os, sys
from common import set_session
from constants import MAI_REDIS_PASSWORD, STR_DISCOVERED_TXS, STR_TX_DISCOVERED,\
    STR_CHANNEL, STR_MESSAGE, STR_TYPE, STR_TXID, STR_RELAYED_FROM,\
    STR_RECEIVED_AT, STR_TIME_RECEIVED, STR_VALUE, STR_VOUT,\
    DEFAULT_LOADING_BATCH_SIZE, DEFAULT_SLEEP_TIME, RESOLVING_POOL_SIZE
import redis
import json
from models import Transaction, TransactionInfo
from datetime import datetime
from pusher import Pusher

class TransactionPusher(Pusher):
    def __init__(self, session,
                 channel = STR_TX_DISCOVERED,
                 queue = STR_DISCOVERED_TXS,
                 batch_size = DEFAULT_LOADING_BATCH_SIZE,
                 sleep_time = DEFAULT_SLEEP_TIME,
                 password = MAI_REDIS_PASSWORD,
                 pool_size = RESOLVING_POOL_SIZE):
        super(TransactionPusher, self).__init__(
            session = session,
            channel = channel,
            queue = queue,
            batch_size = batch_size,
            sleep_time = sleep_time,
            password = password,
            pool_size = pool_size)

    def process_data(self, data):
        result = []
        for datum in data:
            tx_dict = self.__datum_to_tx_dict__(datum)
            tx = Transaction(txid = tx_dict.get(STR_TXID),
                             value = tx_dict.get(STR_VALUE))
            result.append(tx)

            tx_info = TransactionInfo(txid = tx_dict.get(STR_TXID),
                                      relayed_from = tx_dict.get(STR_RELAYED_FROM),
                                      received_at = tx_dict.get(STR_RECEIVED_AT),
                                      json_string = datum)
            result.append(tx_info)
        return result

    def __datum_to_tx_dict__(self, datum):
        result = {}
        if datum:
            result = json.loads(datum)
            result[STR_RECEIVED_AT] = datetime.strptime(result.get(STR_TIME_RECEIVED), '%Y-%m-%d %H:%M:%S')
            result[STR_VALUE] = 0
            for vout_item in result.get(STR_VOUT):
                result[STR_VALUE] = result[STR_VALUE] + vout_item.get(STR_VALUE) 
        return result

    #def __print_loading_message__(self, data):
        #self.print_lock.acquire(True)
     #   print "Done loading transactions:"
        # for datum in data:
        #     tx_dict = __datum_to_tx_dict__(datum)
        #     print '\t', tx_dict
        #self.print_lock.release()

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
    pusher = TransactionPusher(session=session)
    pusher.update_db_transactions()
    