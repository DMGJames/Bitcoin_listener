# Noe installation instructions:
TODO:

# Development Notes:

### Setup Environment 

```
sudo apt-get install python-pip
sudo apt-get install python-mysqldb
sudo apt-get install libmysqlclient-dev
virtualenv venv --distribute
source venv/bin/activate
sudo pip install -r requirement.txt
sh geoip/update.sh
```

Install redis:

```
cd; wget http://download.redis.io/releases/redis-2.8.9.tar.gz
tar xzf redis-2.8.9.tar.gz; cd redis-2.8.9; make; make test
sudo make install
```
Update conf:

```
sudo vi /etc/redis/6379.conf
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

### Update Geo database
`sh bitnodes/geoip/update.sh`

### Auto generate miration script (shound be run on your own dev machine)
`alembic -c ./alembic_local.ini revision  --autogenerate -m "[MESSAGE]"`


### Migration
#### Local
`alembic -c ./alembic_local.ini upgrade head`
#### Test server
`alembic -c ./alembic_test.ini upgrade head`
#### Prod server
`alembic -c alembic_prod.ini upgrade head`


### Run Test

#### Test Model
```
python
import sqlalchemy
from sqlalchemy import create_engine
engine = create_engine('mysql://root:teammaicoin@localhost:3306/listener', echo=True)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()
import models
session.query(models.Node).all() 

```
#### Test uploading nodes via file
`python main.py -n test/nodes_test.txt -e local`

`python main.py -n test/nodes_test.txt -e test`

`python main.py -n test/nodes_test.txt -e prod`

#### Test uploading nodes via redis discovered_nodes
`python main.py -n= -e local`

`python main.py -n= -e test >> pusher.log 2>&1 &`

`python main.py -n= -e prod`


#### Test node_resolver.py
```
python
import node_resolver
node_resolver.__get_raw_geoip__('54.255.25.194')
node_resolver.__get_raw_hostname__('54.255.25.194')
node_resolver.__get_bitcoin_node_info__('86.89.42.107', 8333)
node_resolver.get_node_info('86.89.42.107', 8333)
```

#### Test `__split_address_and_port__`
```
python
from node_pusher import NodePusher
pusher = NodePusher(None)
pusher.__split_address_and_port__('134.43.3.4:1344')
pusher.__split_address_and_port__('134.43:3:4:1344')
pusher.__split_address_and_port__('134.43.3.4')
```

#### Test node loader
`python node_loader.py`

#### Test node pinger
`python node_pinger.py local|test|prod`

#### Test transaction pusher
`python transaction_pusher.py local|test|prod`

### Install bitcoind
git, build....

Add the following in sudo vi /etc/init/bitcoind.conf

```
description "bitcoind"

start on filesystem
stop on runlevel [!2345]
oom never
expect daemon
respawn
respawn limit 10 60 # 10 times in 60 seconds

script
user=ubuntu
home=/home/$user
cmd=/home/$user/listener/src/bitcoind
pidfile=$home/.bitcoin/bitcoind.pid
###### Don't change anything below here unless you know what you're doing
[[ -e $pidfile && ! -d "/proc/$(cat $pidfile)" ]] && rm $pidfile
[[ -e $pidfile && "$(cat /proc/$(cat $pidfile)/cmdline)" != $cmd* ]] && rm $pidfile
exec start-stop-daemon --start -c $user --chdir $home --pidfile $pidfile -b -m --startas $cmd -- -daemon
end script
```

Reload: `sudo initctl reload-configuration`

Start: `sudo start bitcoind`

Stop: `sudo stop bitcoind`

### Deploy node pusher python script
``` 
rsync -Paz --rsync-path "rsync" --exclude "*.pyc" --exclude "*.log" --exclude ".DS_Store" listener_pusher ubuntu@l2:/home/ubuntu/
```

```
rsync -Paz --rsync-path "rsync" --exclude "*.pyc" --exclude "*.log" --exclude ".DS_Store" listener_pusher ubuntu@nva_l1:/home/ubuntu/
```


### Node Pusher Daemon

Test:

```
python node_pusher_daemon_runner.py start local
```

Add the following in sudo vi /etc/init/node_pusher.conf

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


### Node Pinger Daemon
Test:

```
python node_pinger_daemon_runner.py start local
```

Add the following in sudo vi /etc/init/node_pinger.conf

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

### Transaction Pusher Daemon
Test:

```
python transaction_pusher_daemon_runner.py start local

```
Add the following in sudo vi /etc/init/transaction_pusher.conf

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

### Transaction Post Process Daemon
Test:

```
python tx/transaction_post_process_daemon_runner.py start local

```
Add the following in sudo vi /etc/init/transaction_post_process.conf

```
adescription "transaction_post_process"

start on filesystem
stop on runlevel [!2345]
oom never
expect daemon
respawn
respawn limit 10 60 # 10 times in 60 seconds

script
user=ubuntu
home=/home/$user
cmd=/home/$user/listener_pusher/tx/transaction_post_process_daemon_runner.py
pidfile=$home/listener_pusher/transaction_post_process.pid
###### Don't change anything below here unless you know what you're doing
[[ -e $pidfile && ! -d "/proc/$(cat $pidfile)" ]] && rm $pidfile
[[ -e $pidfile && "$(cat /proc/$(cat $pidfile)/cmdline)" != $cmd* ]] && rm $pidfile
exec start-stop-daemon --start -c $user --chdir $home --pidfile $pidfile -b -m --startas $cmd -- start test
end script

```

### Transaction Post Process Cron Job
```
crontab -e
*/10 * * * * cd /home/ubuntu/listener_pusher/ && tx/transaction_post_process.py  test >> /home/ubuntu/listener_pusher/tx_post_process.log
```

### Transaction vin vout Pusher Cron Job and info updater
```
crontab -e
*/15 * * * * cd /home/ubuntu/listener_pusher/ && tx/transaction_vin_vout_pusher.py  test >> /home/ubuntu/listener_pusher/tx_vin_vout_pusher.log && tx/transaction_address_info_updater.py  test >> /home/ubuntu/listener_pusher/tx_address_info_updater.log
````

### Transaction address info updater cron job (deprecated)
```
crontab -e
*/30 * * * * cd /home/ubuntu/listener_pusher/ && tx/transaction_address_info_updater.py  test >> /home/ubuntu/listener_pusher/tx_address_info_updater.log
````

### GeoIP update cron job
```
crontab -e
# Add this line
0 18 * * 1 cd /home/ubuntu/listener_pusher/geoip/ && ./update.sh
```

### Cron job summary
```
0 18 * * 1 cd /home/ubuntu/listener_pusher/geoip/ && ./update.sh
*/10 * * * * cd /home/ubuntu/listener_pusher/ && tx/transaction_post_process.py  test >> /home/ubuntu/listener_pusher/tx_post_process.log
crontab -e
*/15 * * * * cd /home/ubuntu/listener_pusher/ && tx/transaction_vin_vout_pusher.py  test >> /home/ubuntu/listener_pusher/tx_vin_vout_pusher.log
crontab -e
*/15 * * * * cd /home/ubuntu/listener_pusher/ && tx/transaction_vin_vout_pusher.py test >> /home/ubuntu/listener_pusher/tx_vin_vout_pusher.log && tx/transaction_address_info_updater.py test >> /home/ubuntu/listener_pusher/tx_address_info_updater.log

```
### Patch
#### Add transaction type
Fill type filed in transaction model
`python patch/add_transaction_type.py local`

### Post process
#### Transaction post process
Update block_height in transacion
`python tx/transaction_post_process.py local`

### Transaction Adddress pusher
`python tx/transaction_address_pusher.py local`
