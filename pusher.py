'''
Created on Jun 26, 2014

@author: webber
'''
from os.path import os, sys
from constants import MAI_REDIS_PASSWORD, STR_DISCOVERED_TXS, STR_TX_DISCOVERED,\
    STR_CHANNEL, STR_MESSAGE, STR_TYPE, STR_TXID, STR_RELAYED_FROM,\
    STR_RECEIVED_AT, STR_TIME_RECEIVED, STR_VALUE, STR_VOUT,\
    DEFAULT_LOADING_BATCH_SIZE, DEFAULT_SLEEP_TIME, RESOLVING_POOL_SIZE
import redis
import threading
import threadpool
import time

class Pusher(object):
    def __init__(self, session, channel, queue,
                 batch_size = DEFAULT_LOADING_BATCH_SIZE,
                 sleep_time = DEFAULT_SLEEP_TIME,
                 password = MAI_REDIS_PASSWORD,
                 pool_size = RESOLVING_POOL_SIZE):
        self.session = session
        self.channel = channel
        self.queue = queue
        self.batch_size = batch_size
        self.sleep_time = sleep_time
        self.pool = threadpool.ThreadPool(pool_size)
        self.lock = threading.Lock()
        self.print_lock = threading.Lock()

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

    def set_pool_size(pool_size):
        self.pool_size = pool_size

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

    def __load_and_push__(self, dummy):
        print "Start a thread of load_and_push..."
        while self.__has_pending_data__():
            data = self.load_data()
            data = self.process_data(data)
            self.push_data_to_db(data)
            print "sleep ", self.sleep_time
            time.sleep(self.sleep_time)

    def load_and_push(self):
        while self.__has_pending_data__():
            while self.__has_heavy_load__():
                print "workers : queue size ==>",len(self.pool.workers), self.pool._requests_queue.qsize()
                print "sleep 10"
                time.sleep(10)
            requests = threadpool.makeRequests(self.__load_and_push__, [0])
            try:
                for req in requests: self.pool.putRequest(req)
                #self.pool.wait()
            except Exception, e:
                print "Exception on request:", e

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
        self.lock.acquire(True)
        try:
            for datum in data:
                self.session.merge(datum)
            self.session.commit()
            self.__print_pushing_message__(data)
        except Exception, e:
            self.session.rollback()
            print "Exception on pushing new data:", e
        self.lock.release()

    def __has_pending_data__(self):
        return self.redis_connection.llen(self.queue) > 0

    def __has_heavy_load__(self):
        return self.pool._requests_queue.qsize() > len(self.pool.workers)

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

