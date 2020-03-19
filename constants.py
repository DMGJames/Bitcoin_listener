'''
Created on Jun 11, 2014

@author: yutelin, webber
'''
import os

ATTRIBUTE_TIME                    = 'time'
ATTRIBUTE_LAST_NODE_TIMESTAMP     = 'last_node_timestamp'
ATTRIBUTE_NODE                    = 'node'
ATTRIBUTE_CITY                    = 'city'
ATTRIBUTE_COUNTRY_CODE            = 'country_code'
ATTRIBUTE_COUNTRY                 = 'country'
ATTRIBUTE_LATITUDE                = 'latitude'
ATTRIBUTE_LONGITUDE               = 'longitude'
ATTRIBUTE_TIME_ZONE               = 'time_zone'
ATTRIBUTE_ASN                     = 'asn'
ATTRIBUTE_ORG                     = 'org'
ATTRIBUTE_HOSTNAME                = 'hostname'
ATTRIBUTE_USER_AGENT              = 'user_agent'
ATTRIBUTE_VERSION                 = 'version'
ATTRIBUTE_START_HEIGHT            = 'start_height'
ATTRIBUTE_NODE_DATA               = 'node_data'
ATTRIBUTE_ADDRESS                 = 'address'
ATTRIBUTE_IP_ADDRESS              = 'ip_address'
ATTRIBUTE_PORT                    = "port"

ATTRIBUTE_CHANNEL                 = "channel"
ATTRIBUTE_TYPE                    = "type"
ATTRIBUTE_MESSAGE                 = "message"
ATTRIBUTE_ACTIVE                  = "active"
ATTRIBUTE_INACTIVE                = "inactive"
ATTRIBUTE_STATUS                  = "status"

ATTRIBUTE_TXID                    = "txid"
ATTRIBUTE_RELAYED_FROM            = "relayedFrom"
ATTRIBUTE_TIME_RECEIVED           = "timeReceived"
ATTRIBUTE_RECEIVED_AT             = "received_at"
ATTRIBUTE_VALUE                   = "value"
ATTRIBUTE_VIN                     = "vin"
ATTRIBUTE_VOUT                    = "vout"
ATTRIBUTE_SCRIPT_SIG              = "scriptSig"
ATTRIBUTE_SCRIPT_PUB_KEY          = "scriptPubKey"
ATTRIBUTE_BLOCK_HEIGHT            = "block_height"
ATTRIBUTE_BLOCK_HASH              = "block_hash"
ATTRIBUTE_BLOCKHASH               = "blockhash"
ATTRIBUTE_HEIGHT                  = "height"
ATTRIBUTE_MULTISIG                = "multisig"
ATTRIBUTE_NULLDATA                = "nulldata"
ATTRIBUTE_PUBKEY                  = "pubkey"
ATTRIBUTE_PUBKEYHASH              = "pubkeyhash"
ATTRIBUTE_SCRIPTHASH              = "scripthash"
ATTRIBUTE_HAS_MULTISIG            = "has_multisig"
ATTRIBUTE_HAS_NULLDATA            = "has_nulldata"
ATTRIBUTE_HAS_PUBKEY              = "has_pubkey"
ATTRIBUTE_HAS_PUBKEYHASH          = "has_pubkeyhash"
ATTRIBUTE_HAS_SCRIPTHASH          = "has_scripthash"
ATTRIBUTE_JSON_STRING             = "json_string"  
ATTRIBUTE_BLOCK                   = "block"
ATTRIBUTE_HASH                    = "hash"
ATTRIBUTE_TXS                     = "txs"
ATTRIBUTE_N                       = "n"
ATTRIBUTE_ADDRESSES               = "addresses"
ATTRIBUTE_HEIGHT                  = "height"
ATTRIBUTE_COINBASE                = "coinbase"
ATTRIBUTE_ADDED                   = "added"
ATTRIBUTE_REMOVED                 = "removed"
ATTRIBUTE_HEX                     = "hex"


FILENAME_STATE_CFG          = 'state.cfg'
FILENAME_GEO_CITY           = "geoip/GeoLiteCity.dat"
FILENAME_GEO_CITY_V6        = "geoip/GeoLiteCityv6.dat"
FILENAME_GEO_ASN            = "geoip/GeoIPASNum.dat"
FILENAME_GEO_ASN_V6         = "geoip/GeoIPASNumv6.dat" 


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

TX_POST_DAEMON_PID_FILE = '/tmp/transaction-post-process-daemon.pid'
TX_POST_DAEMON_LOG_DIR = os.path.join(file_dir, 'log/transaction-post-process')
TX_POST_DAEMON_STDOUT = os.path.join(TX_POST_DAEMON_LOG_DIR, 'transaction-post-process.log')
TX_POST_DAEMON_STDERR = os.path.join(TX_POST_DAEMON_LOG_DIR, 'transaction-post-process-err.log')

TX_PATCH_DAEMON_PID_FILE = '/tmp/transaction-patch.pid'
TX_PATCH_DAEMON_LOG_DIR = os.path.join(file_dir, 'log/transaction-patch')
TX_PATCH_DAEMON_STDOUT = os.path.join(TX_PATCH_DAEMON_LOG_DIR, 'transaction-patch.log')
TX_PATCH_DAEMON_STDERR = os.path.join(TX_PATCH_DAEMON_LOG_DIR, 'transaction-patch-err.log')

TX_ADDR_INFO_UPDATE_DAEMON_PID_FILE = '/tmp/transaction-addr-info.pid'
TX_ADDR_INFO_UPDATE_DAEMON_LOG_DIR = os.path.join(file_dir, 'log/transaction-addr-info')
TX_ADDR_INFO_UPDATE_DAEMON_STDOUT = os.path.join(TX_ADDR_INFO_UPDATE_DAEMON_LOG_DIR, 'transaction-addr-info.log')
TX_ADDR_INFO_UPDATE_DAEMON_STDERR = os.path.join(TX_ADDR_INFO_UPDATE_DAEMON_LOG_DIR, 'transaction-addr-info-err.log')

DEFAULT_LOADING_BATCH_SIZE      = 5
DEFAULT_SLEEP_TIME              = 0.5
DEFAULT_RESOLVING_POOL_SIZE     = 200
DEFAULT_PINGER_POOL_SIZE        = 200
DEFAULT_TXN_POOL_SIZE           = 200
DEFAULT_MAI_REDIS_PASSWORD      = 'teammaicoin'
DEFAULT_NODE_QUEUE              = "discovered_nodes"
DEFAULT_NODE_CHANNEL            = "node_discovered"
DEFAULT_TX_QUEUE                = "discovered_txs"
DEFAULT_TX_CHANNEL              = "tx_discovered"
DEFAULT_BITCOIND_RPC_URL        = "http://bitcoinrpc:teammaicoin@172.31.28.93:8332"
DEFAULT_LOCAL_BITCONID_RPC_URL  = "http://bitcoinrpc:teamrecon@127.0.0.1:8332"

DEFAULT_TX_ADDRESS_POOL_SIZE    = 1#200

SATOSHI_PER_BTC = 100000000
