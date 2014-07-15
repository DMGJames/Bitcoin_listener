'''
Created on Jul 11, 2014

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
########################################################################
class TransactionVinVoutCsvLoader():
    def __init__(self, txin_file, txout_file, txin_sql_file, txout_sql_file, batch_size = 4000):
        self.batch_size = batch_size
        self.txin_file = txin_file
        self.txout_file = txout_file
        self.txin_sql_file = txin_sql_file
        self.txout_sql_file = txout_sql_file
        self.vin_insert_header = "INSERT INTO `transaction_vin` VALUES "
        self.vout_insert_header = "INSERT INTO `transaction_vout` VALUES "
        
    def start(self):
        print "start"
        print "1. Load txin"
        txin_fd = open(self.txin_file, 'r')
        txin_sql_fd = open(self.txin_sql_file, 'w')
        items = []
        txin_sql_fd.write("LOCK TABLES `transaction_vin` WRITE;\n")
        for line in txin_fd:
            fields = line.rstrip().split(",")
            vout_offset = -1
            vout_offset = '-1'
            if not fields[6] == '1': vout_offset = fields[5]
            txin_tuple = "('%s',%s,'%s',%s,'%s',%s)" % (fields[0],fields[1],fields[4],vout_offset,fields[2],fields[3])
            items.append(txin_tuple)
            if len(items) >= self.batch_size:
                txin_sql = self.vin_insert_header + ",".join(items) + ";\n"
                txin_sql_fd.write(txin_sql)
                items = []
                print "txin:",fields[3]
        txin_sql = self.vin_insert_header + ",".join(items) + ";\n"
        txin_sql_fd.write(txin_sql)
        txin_sql_fd.write("UNLOCK TABLES;")
        items = []

        print "2. Load txout"
        txout_fd = open(self.txout_file, 'r')
        txout_sql_fd = open(self.txout_sql_file , 'w')
        txout_sql_fd.write("LOCK TABLES `transaction_vout` WRITE;\n")
        items = []
        for line in txout_fd:
            fields = line.rstrip().split(",")
            txout_tuple = "('%s',%s,'%s','%s',%s,%s,%s)" % (fields[0],fields[1],fields[2],fields[3],fields[4],fields[5],fields[6])
            items.append(txout_tuple)
            if len(items) >= self.batch_size:
                txout_sql = self.vout_insert_header + ",".join(items) + ";\n"
                txout_sql_fd.write(txout_sql)
                items = []
                print "txout", fields[4]                
        txout_sql = self.vout_insert_header + ",".join(items) + ";\n"
        txout_sql_fd.write(txout_sql)
        txout_sql_fd.write("UNLOCK TABLES;")
        items = []
        
        
env_setting = 'local'
if __name__ == '__main__':
    env_setting = sys.argv[1]
    txin_file = sys.argv[2]
    txout_file = sys.argv[3]
    txin_sql_file = sys.argv[4]
    txout_sql_file = sys.argv[5]
    print "Environment:" , env_setting, txin_file, txout_file, txin_sql_file, txout_sql_file
    ### Pusher
    loader = TransactionVinVoutCsvLoader(txin_file = txin_file, txout_file = txout_file, txin_sql_file=txin_sql_file, txout_sql_file=txout_sql_file)
    loader.start()
    print "Done!"