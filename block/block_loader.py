'''
Created on Jul 21, 2014

@author: yutelin
'''
from bitcoinrpc import proxy
from bitcoinrpc.proxy import AuthServiceProxy

class BlockLoader():
    def __init__(self, rpc_url):
        proxy.HTTP_TIMEOUT = 300
        self.rpc_access = AuthServiceProxy(rpc_url)
    
    def get_block(self, block_height):
        return self.rpc_access.getblockdetail(block_height)
    
    def get_block_count(self):
        return self.rpc_access.getblockcount()
    
    def get_block_sicne(self, block_hash):
        return self.rpc_access.getblocksince(block_hash)
    
    def get_block_txs(self, block_hash):
        return self.rpc_access.getblocktxs(block_hash)