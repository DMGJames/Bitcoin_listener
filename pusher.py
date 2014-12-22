'''
Created on Jun 26, 2014

@author: webber
'''
from constants import DEFAULT_MAI_REDIS_PASSWORD,\
    ATTRIBUTE_CHANNEL, ATTRIBUTE_MESSAGE, ATTRIBUTE_TYPE,\
    DEFAULT_LOADING_BATCH_SIZE, DEFAULT_SLEEP_TIME, DEFAULT_RESOLVING_POOL_SIZE
import redis
import threading
import threadpool
import time
import sys
import os
import gc
from psutil_wrapper import PsutilWrapper

ps = PsutilWrapper(os.getpid())

class Pusher(object):
    def __init__(self, session, channel, queue,
                 batch_size = DEFAULT_LOADING_BATCH_SIZE,
                 sleep_time = DEFAULT_SLEEP_TIME,
                 password = DEFAULT_MAI_REDIS_PASSWORD,
                 pool_size = DEFAULT_RESOLVING_POOL_SIZE):
        self.session = session
        self.channel = channel
        self.queue = queue
        self.batch_size = batch_size
        self.sleep_time = sleep_time
        self.pool = threadpool.ThreadPool(pool_size)
        self.lock = threading.Lock()
        self.print_lock = threading.Lock()

        try:
            self.redis_connection = redis.StrictRedis(port=6378, password=password)
            self.redis_connection.ping()
        except Exception as e:
            sys.exit("ERROR: %s" % e)

    def set_channel(self, channel):
        self.channel = channel

    def set_queue(self, queue):
        self.queue = queue

    def set_batch_size(self, batch_size):
        self.batch_size = batch_size

    def set_session(self, session):
        self.session = session

    def set_sleep_time(self, sleep_time):
        self.sleep_time = sleep_time

    def get_batch_size(self):
        return self.batch_size

    def get_sleep_time(self):
        return self.sleep_time

    def get_pool_size(self):
        return len(self.pool.workers)

    def __num_data_left__(self):
        return self.redis_connection.llen(self.queue)

    def __load_and_push__(self):
        print "Start __load_and_push__..."
        sys.stdout.flush()
        
        while True:
            if self.__has_pending_data__():
                sys.stdout.flush()
                self.__load_and_push_a_batch__()
            else:
                print "sleep", self.sleep_time, "sec"
                sys.stdout.flush()
                time.sleep(self.sleep_time)

    def __load_and_push_a_batch__(self):
        print "Start __load_and_push_a_batch__...({} data left)".format(self.__num_data_left__())
        sys.stdout.flush()
        data = self.load_data()
        data = self.process_data(data)
        self.push_data_to_db(data)

    def __first_try__(self, dummy):
        self.__load_and_push__()

    def start(self):
        self.__print_start_message__()
        for i in range(self.get_pool_size()):
            try:
                requests = threadpool.makeRequests(self.__first_try__, [0])
                for req in requests: self.pool.putRequest(req)
            except Exception as e:
                sys.exit("ERROR: %s" % e)
            self.pool.wait()

    def load_data(self):
        count = 0
        result = []
        while count < self.batch_size and self.redis_connection.llen(self.queue) > 0:
            result.append(self.redis_connection.lpop(self.queue))
            count = count + 1
        self.__print_loading_message__(result)
        return result

    def process_data(self, data):
        # template method
        return data

    def push_data_to_db(self, data):
        self.lock.acquire(True)
        try:
            for datum in data:
                self.session.merge(datum)
            self.session.commit()
            self.__print_pushing_message__(data)
        except Exception as e:
            self.session.rollback()
            print >> sys.stderr, "Exception on pushing new data:", e
        self.lock.release()

    def __has_pending_data__(self):
        return self.__num_data_left__() > 0

    def __has_heavy_load__(self):
        return self.pool._requests_queue.qsize() > len(self.pool.workers)

    def __print_start_message__(self):
        print "Started pusher"
        sys.stdout.flush()

    def __print_loading_message__(self, loaded):
        # template method
        print "Done loading data"
        sys.stdout.flush()

    def __print_pushing_message__(self, pushed):
        # template method
        print "Done pushing data"
        sys.stdout.flush()

