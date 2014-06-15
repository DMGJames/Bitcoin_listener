'''
Created on Jun 11, 2014

@author: yutelin
'''
import os

STR_TIMESTAMP               = 'timestamp'
STR_LAST_NODE_TIMESTAMP     = 'last_node_timestamp'
STR_NODE                    = 'node'
STR_CITY                    = 'city'
STR_COUNTRY_CODE            = 'country_code'
STR_COUNTRY                 = 'country'
STR_LATITUDE                = 'latitude'
STR_LONGITUDE               = 'longitude'
STR_TIME_ZONE               = 'time_zone'
STR_ASN                     = 'asn'
STR_ORG                     = 'org'
STR_HOSTNAME                = 'hostname'
STR_USER_AGENT              = 'user_agent'
STR_VERSION                 = 'version'
STR_START_HEIGHT            = 'start_height'
STR_NODE_DATA               = 'node_data'
STR_IP_ADDRESS              = 'ip_address'
STR_PORT                    = "port"
STR_DISCOVERED_NODES        = "discovered_nodes"
STR_NODE_DISCOVERED         = "node_discovered"
STR_CHANNEL                 = "channel"
STR_TYPE                    = "type"
STR_MESSAGE                 = "message"

FILENAME_STATE_CFG          = 'state.cfg'
FILENAME_GEO_CITY           = "geoip/GeoLiteCity.dat"
FILENAME_GEO_CITY_V6        = "geoip/GeoLiteCityv6.dat"
FILENAME_GEO_ASN            = "geoip/GeoIPASNum.dat"
FILENAME_GEO_ASN_V6         = "geoip/GeoIPASNumv6.dat" 

NODE_LOADING_BATCH_SIZE     = 5
RESOLVING_POOL_SIZE         = 200


NODE_PUSHER_DAEMON_PID_FILE = '/tmp/node-pusher-daemon.pid'
file_dir = os.path.dirname(os.path.realpath(__file__))
NODE_PUSHER_DAEMON_LOG_DIR = os.path.join(file_dir, 'log/node_pusher')
NODE_PUSHER_DAEMON_STDOUT = os.path.join(NODE_PUSHER_DAEMON_LOG_DIR, 'node-pusher.log')
NODE_PUSHER_DAEMON_STDERR = os.path.join(NODE_PUSHER_DAEMON_LOG_DIR, 'node-pusher-err.log')