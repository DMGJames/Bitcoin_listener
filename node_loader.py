'''
Created on Jun 12, 2014

@author: yutelin
'''
import redis
from constants import STR_DISCOVERED_NODES, NODE_LOADING_BATCH_SIZE,\
    STR_NODE_DISCOVERED, STR_CHANNEL, STR_TYPE, STR_MESSAGE, RESOLVING_POOL_SIZE,\
    MAI_REDIS_PASSWORD
import threadpool
import time



class NodeLoader:
    def __init__(self):
        try:
            self.redis_connection =  redis.StrictRedis(password=MAI_REDIS_PASSWORD)
            self.redis_connection.ping()
        except:
            self.redis_connection =  redis.StrictRedis()
        self.pool = threadpool.ThreadPool(RESOLVING_POOL_SIZE)

    def load_nodes(self):
        count = 0
        result = []
        while count < NODE_LOADING_BATCH_SIZE and self.redis_connection.llen(STR_DISCOVERED_NODES) > 0:
            result.append(self.redis_connection.lpop(STR_DISCOVERED_NODES))
            count = count+1
        print "load nodes", result
        return result

    def __load_and_push_nodes_in_redis__(self, node_pusher):
        node_ips = self.load_nodes()
        while len(node_ips) > 0:
            while self.pool._requests_queue.qsize() > len(self.pool.workers) :
                print "workers: queue size ==>",len(self.pool.workers), self.pool._requests_queue.qsize()
                print "sleep 0.5"
                time.sleep(0.5)
            requests = threadpool.makeRequests(node_pusher.update_db_nodes_with_node_ips, [node_ips])
            try:
                for req in requests: self.pool.putRequest(req)
            except Exception, e:
                print "Exception on request:", e
            #node_pusher.update_db_nodes_with_node_ips(node_ips = node_ips)
            node_ips = self.load_nodes()

    def load_and_push_nodes(self, node_pusher):
        #1. Try to load_nodes first
        self.__load_and_push_nodes_in_redis__(node_pusher = node_pusher);
                
        #2. Listen to channel then
        pubsub = self.redis_connection.pubsub()
        pubsub.subscribe(STR_NODE_DISCOVERED)
        for msg in pubsub.listen():
            if msg[STR_CHANNEL] == STR_NODE_DISCOVERED and msg[STR_TYPE] == STR_MESSAGE:
                #timestamp = int(msg['data'])
                self.__load_and_push_nodes_in_redis__(node_pusher = node_pusher);
        return 0

if __name__ == '__main__':
    #nodes = load_nodes()
    loader = NodeLoader()
    nodes = loader.load_nodes()
    print nodes
    