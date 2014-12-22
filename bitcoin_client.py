'''
Created on Jul 21, 2014

@author: yutelin
'''
from bitcoinrpc import proxy
from bitcoinrpc.proxy import AuthServiceProxy

class BitcoinClient():
    def __init__(self, rpc_url):
        proxy.HTTP_TIMEOUT = 300
        self.rpc_url = rpc_url

    def __getattr__(self, name):
        return AuthServiceProxy(self.rpc_url, name)
