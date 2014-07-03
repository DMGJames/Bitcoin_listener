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
from models import Transaction, TransactionInfo
import json
from constants import ATTRIBUTE_TYPE, ATTRIBUTE_VOUT, ATTRIBUTE_SCRIPT_PUB_KEY,\
    ATTRIBUTE_MULTISIG, ATTRIBUTE_NULLDATA, ATTRIBUTE_PUBKEY,\
    ATTRIBUTE_PUBKEYHASH, ATTRIBUTE_SCRIPTHASH, ATTRIBUTE_JSON_STRING,\
    ATTRIBUTE_TXID

class AddScriptPubKeyPatch():
    def __init__(self, query_session, update_session):
        self.query_session = query_session
        self.update_session = update_session
        
    def run_patch(self):
        print "run patch"
        # 1. Get all transactions
        limit = 200
        offset = 0
        while True:
            txs = self.query_session.query(Transaction.txid).filter(Transaction.has_multisig == None).order_by(Transaction.txid).offset(offset).limit(limit)
            txids = [tx.txid for tx in txs]
            if len(txids) == 0: break
            print "limit:offset", limit, offset
            tx_infos = self.query_session.query(TransactionInfo).filter(TransactionInfo.txid.in_(txids))
            tx_info_dicts = [tx_info.__dict__ for tx_info in tx_infos]
            update_count = 0
            for tx_info_dict in tx_info_dicts:
                if tx_info_dict.get(ATTRIBUTE_JSON_STRING):
                    try:
                        tx_info_json_dict = json.loads(tx_info_dict.get(ATTRIBUTE_JSON_STRING))
                        vouts = tx_info_json_dict[ATTRIBUTE_VOUT]
                        has_multisig = has_nulldata = has_pubkey = has_pubkeyhash = has_scripthash = False
                        #print "txid:", tx_info_dict.get(ATTRIBUTE_TXID)
                        for vout in vouts:
                            script_type = vout[ATTRIBUTE_SCRIPT_PUB_KEY][ATTRIBUTE_TYPE]
                            #print "script_type:", script_type
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
                        print has_multisig,has_nulldata,has_pubkey,has_pubkeyhash,has_scripthash
                        self.update_session.query(Transaction).filter(Transaction.txid == tx_info_dict.get(ATTRIBUTE_TXID)).update(
                                   {Transaction.has_multisig:has_multisig,
                                    Transaction.has_nulldata:has_nulldata,
                                    Transaction.has_pubkey:has_pubkey,
                                    Transaction.has_pubkeyhash:has_pubkeyhash,
                                    Transaction.has_scripthash:has_scripthash})
                        update_count = update_count + 1
                    except Exception, e:
                        print "Exception (ignored):",e
            #if update_count>0:
            self.update_session.commit()
            if(txs.count() > 0):
                offset=offset+limit
            else:
                break
        print "Done"

if __name__ == '__main__':
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    query_session = set_session(env_setting=env_setting)
    update_session = set_session(env_setting=env_setting)
    patch = AddScriptPubKeyPatch(query_session=query_session, update_session=update_session)
    patch.run_patch()
    