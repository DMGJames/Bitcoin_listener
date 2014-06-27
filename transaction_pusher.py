'''
Created on Jun 19, 2014

@author: yutelin
'''
from os.path import os, sys
from common import set_session
from constants import MAI_REDIS_PASSWORD, STR_DISCOVERED_TXS, STR_TX_DISCOVERED,\
    STR_CHANNEL, STR_MESSAGE, STR_TYPE, STR_TXID, STR_RELAYED_FROM,\
    STR_RECEIVED_AT, STR_TIME_RECEIVED, STR_VALUE, STR_VOUT
import redis
import json
from models import Transaction, TransactionInfo
from datetime import datetime

class TransactionPusher():
    def __init__(self, session_fn):
        self.session_fn = session_fn
        self.session = self.session_fn()
        try:
            self.redis_connection =  redis.StrictRedis(password=MAI_REDIS_PASSWORD)
            self.redis_connection.ping()
        except:
            self.redis_connection =  redis.StrictRedis()

    
    def update_db_transactions(self):
        #1. Try to save existing transactions
        self.__load_all_transactions_and_update_db__()
        
        #2. Listen to channel then
        pubsub = self.redis_connection.pubsub()
        pubsub.subscribe(STR_TX_DISCOVERED)
        for msg in pubsub.listen():
            if msg[STR_CHANNEL] == STR_TX_DISCOVERED and msg[STR_TYPE] == STR_MESSAGE:
                self.__load_all_transactions_and_update_db__()
        return 0
        
    def __load_transaction__(self):
        result = None
        if self.redis_connection.llen(STR_DISCOVERED_TXS) > 0:
            result=self.redis_connection.lpop(STR_DISCOVERED_TXS)
        return result
    
    def __transaction_to_dict__(self, txn):
        result = {}
        if txn:
            result = json.loads(txn)
            result[STR_RECEIVED_AT] = datetime.strptime(result.get(STR_TIME_RECEIVED), '%Y-%m-%d %H:%M:%S')
            result[STR_VALUE] = 0
            for vout_item in result.get(STR_VOUT):
                result[STR_VALUE] = result[STR_VALUE] + vout_item.get(STR_VALUE) 
        return result

    def __load_transaction_and_update_db__(self):
        #1. Load oldest transaction
        txn = self.__load_transaction__()
        if txn:
            txn_dict = self.__transaction_to_dict__(txn = txn)
            #print txn_dict
            #2. Save it to "transaction" table if doesn't exist
            try: 
                transaction = Transaction(txid = txn_dict.get(STR_TXID),
                                          value = txn_dict.get(STR_VALUE)
                                          )
                self.session.merge(transaction)
                self.session.commit()
                print "Added transaction:", transaction.txid
            except Exception, e:
                self.session.rollback()
                print "Exception on adding new transaction:", txn_dict.get(STR_TXID), e
            finally:
                self.session.close()
            
            #3. Save detail info to "transaction_info" table
            try:                 
                transaction_info = TransactionInfo(txid = txn_dict.get(STR_TXID),
                                                   relayed_from = txn_dict.get(STR_RELAYED_FROM),
                                                   received_at = txn_dict.get(STR_RECEIVED_AT),
                                                   json_string = txn)
                self.session.merge(transaction_info)
                self.session.commit()
                print "Added transaction info:", transaction_info.txid, transaction_info.relayed_from 
            except Exception, e:
                self.session.rollback()
                print "Exception on adding new transaction:", txn_dict.get(STR_TXID), e
            finally:
                self.session.close()
        return txn
    
    def __load_all_transactions_and_update_db__(self):
        while self.__load_transaction_and_update_db__() != None:
            break
            #continue

def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(file_dir)

if __name__ == '__main__':
    set_env()
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    session_fn = set_session(env_setting=env_setting)
    pusher = TransactionPusher(session_fn=session_fn)
    pusher.update_db_transactions()
    