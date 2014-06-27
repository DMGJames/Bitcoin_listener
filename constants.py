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
STR_ADDRESS                 = 'address'
STR_IP_ADDRESS              = 'ip_address'
STR_PORT                    = "port"
STR_DISCOVERED_NODES        = "discovered_nodes"
STR_NODE_DISCOVERED         = "node_discovered"
STR_CHANNEL                 = "channel"
STR_TYPE                    = "type"
STR_MESSAGE                 = "message"
STR_ACTIVE                  = "active"
STR_INACTIVE                = "inactive"
STR_STATUS                  = "status"
STR_DISCOVERED_TXS          = "discovered_txs"
STR_TX_DISCOVERED           = "tx_discovered"
STR_TXID                    = "txid"
STR_RELAYED_FROM            = "relayedFrom"
STR_TIME_RECEIVED           = "timeReceived"
STR_RECEIVED_AT             = "received_at"
STR_VALUE                   = "value"
STR_VOUT                    = "vout"


FILENAME_STATE_CFG          = 'state.cfg'
FILENAME_GEO_CITY           = "geoip/GeoLiteCity.dat"
FILENAME_GEO_CITY_V6        = "geoip/GeoLiteCityv6.dat"
FILENAME_GEO_ASN            = "geoip/GeoIPASNum.dat"
FILENAME_GEO_ASN_V6         = "geoip/GeoIPASNumv6.dat" 

NODE_LOADING_BATCH_SIZE     = 5
RESOLVING_POOL_SIZE         = 200
PINGER_POOL_SIZE            = 200

MAI_REDIS_PASSWORD          = 'teammaicoin'

file_dir = os.path.dirname(os.path.realpath(__file__))
NODE_PUSHER_DAEMON_PID_FILE = '/tmp/node-pusher-daemon.pid'
NODE_PUSHER_DAEMON_LOG_DIR = os.path.join(file_dir, 'log/node_pusher')
NODE_PUSHER_DAEMON_STDOUT = os.path.join(NODE_PUSHER_DAEMON_LOG_DIR, 'node-pusher.log')
NODE_PUSHER_DAEMON_STDERR = os.path.join(NODE_PUSHER_DAEMON_LOG_DIR, 'node-pusher-err.log')

NODE_PINGER_DAEMON_PID_FILE = '/tmp/node-pinger-daemon.pid'
NODE_PINGER_DAEMON_LOG_DIR = os.path.join(file_dir, 'log/node_pinger')
NODE_PINGER_DAEMON_STDOUT = os.path.join(NODE_PINGER_DAEMON_LOG_DIR, 'node-pinger.log')
NODE_PINGER_DAEMON_STDERR = os.path.join(NODE_PINGER_DAEMON_LOG_DIR, 'node-pinger-err.log')

TX_PUSHER_DAEMON_PID_FILE = '/tmp/transaction-pusher-daemon.pid'
TX_PUSHER_DAEMON_LOG_DIR = os.path.join(file_dir, 'log/transaction_pusher')
TX_PUSHER_DAEMON_STDOUT = os.path.join(TX_PUSHER_DAEMON_LOG_DIR, 'transaction-pusher.log')
TX_PUSHER_DAEMON_STDERR = os.path.join(TX_PUSHER_DAEMON_LOG_DIR, 'transaction-pusher-err.log')