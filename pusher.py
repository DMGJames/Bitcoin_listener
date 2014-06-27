'''
Created on Jun 26, 2014

@author: webber
'''
from os.path import os, sys
from constants import MAI_REDIS_PASSWORD, STR_DISCOVERED_TXS, STR_TX_DISCOVERED,\
    STR_CHANNEL, STR_MESSAGE, STR_TYPE, STR_TXID, STR_RELAYED_FROM,\
    STR_RECEIVED_AT, STR_TIME_RECEIVED, STR_VALUE, STR_VOUT,\
    DEFAULT_LOADING_BATCH_SIZE, DEFAULT_SLEEP_TIME
import redis
import time

class Pusher(object):
    def __init__(self, session, channel, queue,
                 batch_size = DEFAULT_LOADING_BATCH_SIZE,
                 sleep_time = DEFAULT_SLEEP_TIME,
                 password = MAI_REDIS_PASSWORD):
        self.session = session
        self.channel = channel
        self.queue = queue
        self.batch_size = batch_size
        self.sleep_time = sleep_time

        try:
            self.redis_connection =  redis.StrictRedis(password = password)
            self.redis_connection.ping()
        except:
            self.redis_connection =  redis.StrictRedis()

    def set_channel(channel):
        self.channel = channel

    def set_queue(queue):
        self.queue = queue

    def set_batch_size(batch_size):
        self.batch_size = batch_size

    def set_session(session):
        self.session = session

    def set_sleep_time(sleep_time):
        self.sleep_time = sleep_time

    def start(self):
        self.load_and_push()
        self.listen()

    def listen(self):
        print "Start listening..."
        pubsub = self.redis_connection.pubsub()
        pubsub.subscribe(self.channel)
        for msg in pubsub.listen():
            if msg[STR_CHANNEL] == self.channel and msg[STR_TYPE] == STR_MESSAGE:
                self.load_and_push()
        return 0

    def load_and_push(self):
        print "Start load_and_push..."
        while self.redis_connection.llen(self.queue) > 0:
            data = self.load_data()
            data = self.process_data(data)
            self.push_data_to_db(data)
            print "sleep ", self.sleep_time
            time.sleep(self.sleep_time)

    def load_data(self):
        count = 0
        result = []
        while count < self.batch_size and self.redis_connection.llen(self.queue) > 0:
            result.append(self.redis_connection.lpop(self.queue))
            count = count + 1
        self.__print_loading_message__(result)
        return result

    def process_data(self, data):
        """
        You must override this method when you subclass Loader or it will
        do nothing but return the date by default
        """
        return data

    def push_data_to_db(self, data):
        """
        You must override this method when you subclass Loader.
        """
        try:
            for datum in data:
                self.session.merge(datum)
            self.session.commit()
            self.__print_pushing_message__(data)
        except Exception, e:
            self.session.rollback()
            print "Exception on pushing new data:", e

    def __print_loading_message__(self, loaded):
        """
        You may override this method when you subclass Loader.
        """
        print "Done loading data"

    def __print_pushing_message__(self, pushed):
        """
        You may override this method when you subclass Loader.
        """
        print "Done pushing data"

