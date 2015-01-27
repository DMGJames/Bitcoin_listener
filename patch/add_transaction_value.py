'''
Created on Jul 1, 2014

@author: yutelin
'''
##### Set environment #####
import os
from os.path import sys
def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    # sys.path.append(file_dir)
    sys.path.append(file_dir + "/../")
    print sys.path
set_env()

######################################################################## 
from common import set_session
from models import RawTransaction, RawTransactionInfo
import json
from constants import ATTRIBUTE_VOUT, ATTRIBUTE_JSON_STRING, ATTRIBUTE_VALUE,\
    ATTRIBUTE_TXID

class AddValuePatch():
    def __init__(self, query_session, update_session):
        self.query_session = query_session
        self.update_session = update_session
        
    def run_patch(self):
        print "run patch"
        # 1. Get all transactions
        limit = 200
        offset = 0
        while True:
            txs = self.query_session.query(RawTransaction.txid).filter(RawTransaction.value == None).order_by(RawTransaction.txid).offset(offset).limit(limit)
            txids = [tx.txid for tx in txs]
            if len(txids) == 0: break
            print "limit:offset", limit, offset
            tx_infos = self.query_session.query(RawTransactionInfo).filter(RawTransactionInfo.txid.in_(txids))
            tx_info_dicts = [tx_info.__dict__ for tx_info in tx_infos]
            update_count = 0
            for tx_info_dict in tx_info_dicts:
                if tx_info_dict.get(ATTRIBUTE_JSON_STRING):
                    try:
                        tx_info_json_dict = json.loads(tx_info_dict.get(ATTRIBUTE_JSON_STRING))
                        vouts = tx_info_json_dict[ATTRIBUTE_VOUT]
                        value = 0
                        #print "txid:", tx_info_dict.get(ATTRIBUTE_TXID)
                        for vout in vouts:
                            print "plus:",vout.get(ATTRIBUTE_VALUE, 0)
                            value = value + vout.get(ATTRIBUTE_VALUE, 0)
                        print "value:", value
                        self.update_session.query(RawTransaction).filter(RawTransaction.txid == tx_info_dict.get(ATTRIBUTE_TXID)).update(
                                   {RawTransaction.value:value})
                        update_count = update_count + 1
                    except Exception, e:
                        print "Exception (ignored):",e
            self.update_session.commit()
            if(txs.count() > 0):
                offset=offset+limit
            else:
                break
        print "Done!"

if __name__ == '__main__':
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    query_session = set_session(env_setting=env_setting)
    update_session = set_session(env_setting=env_setting)
    patch = AddValuePatch(query_session=query_session, update_session=update_session)
    patch.run_patch()
    