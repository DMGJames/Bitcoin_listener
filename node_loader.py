'''
Created on Jun 12, 2014

@author: yutelin
'''
import redis
from constants import STR_DISCOVERED_NODES, NODE_LOADING_BATCH_SIZE,\
    STR_NODE_DISCOVERED, STR_CHANNEL, STR_TYPE, STR_MESSAGE
redis_connection =  redis.StrictRedis()

def load_nodes():
    count = 0
    result = []
    while count < NODE_LOADING_BATCH_SIZE and redis_connection.llen(STR_DISCOVERED_NODES) > 0:
        result.append(redis_connection.lpop(STR_DISCOVERED_NODES))
        count = count+1
    print "load nodes", result
    return result

def load_and_push_nodes(node_pusher):
    pubsub = redis_connection.pubsub()
    pubsub.subscribe(STR_NODE_DISCOVERED)
    for msg in pubsub.listen():
        if msg[STR_CHANNEL] == STR_NODE_DISCOVERED and msg[STR_TYPE] == STR_MESSAGE:
            #timestamp = int(msg['data'])
            node_ips = load_nodes()
            node_pusher.update_db_nodes_with_node_ips(node_ips = node_ips)
    return 0

if __name__ == '__main__':
    nodes = load_nodes()
    