# database-api

API to create, list and delete etcd database instances running in AWS. It uses default VPC/Subnet/SecurityGroup

before to run:
- create .aws/credentials file inside the repo with access and secret keys 

to run the api:
- docker build -t db-api .
- docker run -ti -p 8080:8080 -e "TOKEN1=<token-id>" db-api

to get databases:
- curl -X GET -H "X-AUTH: <token-id>" http://localhost:8080/databases

to create database:
- curl -X POST -H "X-AUTH: <token-id>" --header "Content-Type: application/json" localhost:8080/databases -d '{"name": "database1", "plan": "t2.micro"}'

to delete database:
- curl -X DELETE -H "X-AUTH: <token-id>" http://localhost:8080/databases/<instance-id>

to test etcd after create database:
- open port 2379 in security group from source required
- etcdctl --endpoints http://<public_instance_ip>:2379 mk </path/key> <value>
- etcdctl --endpoints http://<public_instance_ip>:2379 ls


