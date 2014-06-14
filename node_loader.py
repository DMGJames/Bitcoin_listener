'''
Created on Jun 12, 2014

@author: yutelin
'''
import redis
from constants import STR_DISCOVERED_NODES, NODE_LOADING_BATCH_SIZE,\
    STR_NODE_DISCOVERED, STR_CHANNEL, STR_TYPE, STR_MESSAGE
redis_connection =  redis.StrictRedis(password='teammaicoin')

def load_nodes():
    count = 0
    result = []
    while count < NODE_LOADING_BATCH_SIZE and redis_connection.llen(STR_DISCOVERED_NODES) > 0:
        result.append(redis_connection.lpop(STR_DISCOVERED_NODES))
        count = count+1
    print "load nodes", result
    return result

def __load_and_push_nodes_in_redis__(node_pusher):
    node_ips = load_nodes()
    while len(node_ips) > 0:
        node_pusher.update_db_nodes_with_node_ips(node_ips = node_ips)
        node_ips = load_nodes()

def load_and_push_nodes(node_pusher):
    #1. Try to load_nodes first
    __load_and_push_nodes_in_redis__(node_pusher = node_pusher);
            
    #2. Listen to channel then
    pubsub = redis_connection.pubsub()
    pubsub.subscribe(STR_NODE_DISCOVERED)
    for msg in pubsub.listen():
        if msg[STR_CHANNEL] == STR_NODE_DISCOVERED and msg[STR_TYPE] == STR_MESSAGE:
            #timestamp = int(msg['data'])
            __load_and_push_nodes_in_redis__(node_pusher = node_pusher);
    return 0

if __name__ == '__main__':
    nodes = load_nodes()
    