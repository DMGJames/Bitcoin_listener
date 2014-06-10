### Setup Environment 
`virtualenv venv --distribute`

`source venv/bin/activate`

`pip install -r requirements.txt`


### Auto generate miration script
`alembic revision --autogenerate -m "Create node table"`


### Migration
`alembic upgrade head`


### Run Test
#### Test uploading nodes
`python main.py -n test/nodes_test.txt`