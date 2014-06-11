### Setup Environment 
`virtualenv venv --distribute`

`source venv/bin/activate`

`pip install -r requirements.txt`

`sh geoip/update.sh`


### Update Geo database
`sh bitnodes/geoip/update.sh`

### Auto generate miration script
`alembic revision --autogenerate -m "[MESSAGE]"`


### Migration
`alembic upgrade head`


### Run Test
#### Test uploading nodes
`python main.py -n test/nodes_test.txt`

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

