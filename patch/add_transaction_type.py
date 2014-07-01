'''
Created on Jun 28, 2014

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
from constants import ATTRIBUTE_TYPE, ATTRIBUTE_VOUT, ATTRIBUTE_SCRIPT_PUB_KEY

class AddTransactionTypePatch():
    def __init__(self, session):
        self.session = session
        
    def run_patch(self):
        print "run patch"
        # 1. Get all transactions
        txs = self.session.query(Transaction).filter(Transaction.type == None).all()
        count = 0
        for tx in txs:
            try:
                tx_info = self.session.query(TransactionInfo). \
                    filter(TransactionInfo.txid == tx.txid).first()
                if tx_info and tx_info.json_string :
                    tx_info_dict = json.loads(tx_info.json_string)
                    
                    tx.type = tx_info_dict[ATTRIBUTE_VOUT][0][ATTRIBUTE_SCRIPT_PUB_KEY][ATTRIBUTE_TYPE]
                    print "Update:", tx.txid, "to:", tx.type
                    self.session.merge(tx)
                    self.session.commit()
                    count = count + 1
            except Exception, e:
                print "Exception on processing:", tx.txid, e
        print "Update:", count

if __name__ == '__main__':
    env_setting = sys.argv[1]
    print "Environment:" , env_setting
    session = set_session(env_setting=env_setting)
    patch = AddTransactionTypePatch(session=session)
    patch.run_patch()
    
