Last updated (12/23/2014)

# Components

There are 6 components:

1. Listener - the modified bitcoin C++ source code which is used to track the data from the network. Currently we push all node and transaction data to redis, so other program and read it and perform further operation.
1. NodePusher - read node data from redis and push it to RDS. Listener dependency.
1. TransactionPusher - read transaction data from redis and put it to RDS. Listener dependency. 
1. NodePinger - find all nodes from RDS with non-NULL user_agent fields and ping those nodes constantly to see if they are active. We should put this component in a dedicated instance to avoid being backlisted. (Meaning no bitcoind or other scripts running)
1. AddIncrementalBlocks - update blockchain since the last block found in the database
1. TransactionPostProcess - update block information for transaction data pushed by TransactionPusher. The block information could be missing because those pushed transactions are raw transactions. They might have not been packed in blocks while being pushed.  

---

## Common
* Launch a latest ubuntu instance on AWS. Give enough space, say 48GB.

	**Note: if you are running instances in a different zone of the RDS, you probably need to authroize that IP.**


* Update apt-get

	`sudo apt-get udpate`


* Install packages

 	`sudo apt-get install make`
 	
	`sudo apt-get -q -y install gcc `
	
	`sudo apt-get -q -y install git`

* Copy key
	
	Copy your keys to .ssh folder



---


## Listener
### Install redis
Go http://download.redis.io/releases/ and find the latest release. Run the following with necessary version change.

`sudo apt-get -q -y install redis-server`

Edit setting:

```
sudo vi /etc/redis/redis.conf
#### Append the following
aof-rewrite-incremental-fsync yes
requirepass teammaicoin
maxclients 50000
maxmemory 32212254720
maxmemory-policy volatile-ttl
appendfsync no
activerehashing no
hz 30
```

Restart redis:

`sudo /etc/init.d/redis-server restart`

Link redis: if doens't exist

`sudo ln -s /usr/bin/redis-cli /usr/local/bin`

### Install dependencies
Add one line in `sudo vi /etc/apt/sources.list`

`deb http://ftp.de.debian.org/debian squeeze main `

And run

`sudo apt-get update`

Install packages:

```
sudo apt-get -q -y install build-essential
sudo apt-get -q -y install libtool autotools-dev autoconf
sudo apt-get -q -y install libssl-dev
sudo apt-get -q -y install libboost-all-dev
sudo apt-get -q -y install libdb4.8-dev --force-yes
sudo apt-get -q -y install libdb4.8++-dev --force-yes
sudo apt-get install libboost1.55-all-dev 
# if it fails run sudo apt-get install libboost1.55-dev frist.
sudo apt-get -q -y install libminiupnpc-dev 
```

### Compile bitcoind

Download the code

```

sudo apt-get install pkg-config
git clone git@github.com:huuep/listener.git
cd listener
git checkout -b listener-node-collector remotes/origin/listener-node-collector
./autogen.sh
./configure
make
```

### Edit bitcion settings

```
src/bitcoind -help
vi ~/.bitcoin/bitcoin.conf
#add this
rpcuser=bitcoinrpc
rpcpassword=151500d4d1a4750911109bf57928ec93
```

---

## NodePusher
### Install required packages
```
sudo apt-get -q -y install mysql-client
sudo apt-get -q -y install python-pip
sudo apt-get -q -y install python-mysqldb
sudo apt-get -q -y install libmysqlclient-dev
```

### Download source code

```
git clone git@github.com:huuep/listener_pusher.git
##### Switch to what branch that fits
cd listener_pusher
git branch -r
git checkout -b 72_add_node_collection origin/72_add_node_collection
sudo pip install -r requirement.txt
git submodule init
git submodule update
cd geoip
sh geoip/update.sh
```

### Test running:
`python main.py -n= -e test`

### Add cron job to update geoip
```
crontab -e
# Add this line
0 18 * * 1 cd /home/ubuntu/listener_pusher/geoip/ && ./update.sh
```

### Add to daemon

Add the following in `sudo vi /etc/init/node_pusher.conf`

```
description "node_pusher"

start on filesystem
stop on runlevel [!2345]
oom never
expect daemon
respawn
respawn limit 10 60 # 10 times in 60 seconds

script
user=ubuntu
home=/home/$user
cmd=/home/$user/listener_pusher/node_pusher_daemon_runner.py
pidfile=$home/listener_pusher/node_pusher.pid
######### Don't change anything below here unless you know what you're doing
[[ -e $pidfile && ! -d "/proc/$(cat $pidfile)" ]] && rm $pidfile
[[ -e $pidfile && "$(cat /proc/$(cat $pidfile)/cmdline)" != $cmd* ]] && rm $pidfile
exec start-stop-daemon --start -c $user --chdir $home --pidfile $pidfile -b -m --startas $cmd -- start test
end script
```

Reload: `sudo initctl reload-configuration`

Start: `sudo start node_pusher`

Run it manually: `python node_pusher_daemon_runner.py start test`

Check the logs in log folder

### Results
The node data are pushed from redis queue to table *node*.

---
## TransactionPusher
Go through NodePusher installation and source code download.

### Test running:

`python transaction_pusher.py test`

### Add to daemon

Add the following in `sudo vi /etc/init/transaction_pusher.conf`

```
description "transaction_pusher"

start on filesystem
stop on runlevel [!2345]
oom never
expect daemon
respawn
respawn limit 10 60 # 10 times in 60 seconds

script
user=ubuntu
home=/home/$user
cmd=/home/$user/listener_pusher/transaction_pusher_daemon_runner.py
pidfile=$home/listener_pusher/transaction_pusher.pid
###### Don't change anything below here unless you know what you're doing
[[ -e $pidfile && ! -d "/proc/$(cat $pidfile)" ]] && rm $pidfile
[[ -e $pidfile && "$(cat /proc/$(cat $pidfile)/cmdline)" != $cmd* ]] && rm $pidfile
exec start-stop-daemon --start -c $user --chdir $home --pidfile $pidfile -b -m --startas $cmd -- start test
end script

```

Reload: `sudo initctl reload-configuration`

Start: `sudo start transaction_pusher`

Run it manually: `python transaction_pusher_daemon_runner.py start test`

Check the logs in log folder

### Results

The transaction date are pushed from redis queue to tables *transaction* and *transaction_info*.

---

## NodePinger
Go through NodePusher installation and source code download.

### Test running:

`python node_pinger.py test`

### Add to daemon

Add the following in `sudo vi /etc/init/node_pinger.conf`

```
description "node_pinger"

start on filesystem
stop on runlevel [!2345]
oom never
expect daemon
respawn
respawn limit 10 60 # 10 times in 60 seconds

script
user=ubuntu
home=/home/$user
cmd=/home/$user/listener_pusher/node_pinger_daemon_runner.py
pidfile=$home/listener_pusher/node_pinger.pid
###### Don't change anything below here unless you know what you're doing
[[ -e $pidfile && ! -d "/proc/$(cat $pidfile)" ]] && rm $pidfile
[[ -e $pidfile && "$(cat /proc/$(cat $pidfile)/cmdline)" != $cmd* ]] && rm $pidfile
exec start-stop-daemon --start -c $user --chdir $home --pidfile $pidfile -b -m --startas $cmd -- start test
end script
```

Reload: `sudo initctl reload-configuration`

Start: `sudo start node_pinger`

Run it manually: `python node_pinger_daemon_runner.py start test`

Check the logs in log folder

### Results

The activities of nodes being pinged are pushed to table *node_activity*.

---

## AddIncrementalBlocks

### Add to crontab

For example, add the following in crontab:

`*/10 * * * * cd /home/mcdeploy/listener_pusher/current && block/add_incremental_blocks.py prod `

Run it manually: `python add_incremental_blocks.py prod`

### Results

The blockchain info&mdash;recorded in tables *blocks*, *transactions*, *inputs*, and *outputs*&mdash;is updated.

---

## TransactionPostProcess

### Add to crontab

For example, add the following in crontab:

`*/10 * * * * cd /home/mcdeploy/listener_pusher/current && tx/transaction_post_process.py prod `

Run it manually: `python transaction_post_process.py prod`

### Results

The attributes *block_height* and *block_hash* in table *transaction* are updated if available.



