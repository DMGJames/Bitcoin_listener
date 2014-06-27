'''
Created on Jun 26, 2014

@author: webber
'''
from os.path import os, sys
from constants import MAI_REDIS_PASSWORD, STR_DISCOVERED_TXS, STR_TX_DISCOVERED,\
    STR_CHANNEL, STR_MESSAGE, STR_TYPE, STR_TXID, STR_RELAYED_FROM,\
    STR_RECEIVED_AT, STR_TIME_RECEIVED, STR_VALUE, STR_VOUT
import redis

class Pusher(object):
    def __init__(self, password, channel, queue, batch_size):
        self.channel = channel
        self.queue = queue
        self.batch_size = batch_size

        try:
            self.redis_connection =  redis.StrictRedis(password = password)
            self.redis_connection.ping()
        except:
            self.redis_connection =  redis.StrictRedis()

    def listen(self):
        pubsub = self.redis_connection.pubsub()
        pubsub.subscribe(self.channel)
        for msg in pubsub.listen():
            if msg[STR_CHANNEL] == self.channel and msg[STR_TYPE] == STR_MESSAGE:
                self.load_and_push()
        return 0

    def load_and_push(self):
        data = self.load_data()
        self.push(data)

    def load_data(self):
        count = 0
        result = []
        while count < self.batch_size and self.redis_connection.llen(self.queue) > 0:
            result.append(self.redis_connection.lpop(self.queue))
            count = count + 1
        self.__print_loading_message__(result)
        result = self.process_data(result)
        return result

    def process_data(self, data):
        """
        You must override this method when you subclass Loader or it will
        do nothing but return the date by default
        """
        return data

    def push_data_to_db(self):
        """
        You must override this method when you subclass Loader.
        """

    def __print_loading_message__(self, loaded):
        """
        You may override this method when you subclass Loader.
        """
        pass

