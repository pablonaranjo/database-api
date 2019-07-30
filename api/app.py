#!/bin/python
from flask import Flask, request, abort
import boto3
from botocore.exceptions import ClientError
import json, os

app = Flask(__name__)
aws_session = boto3.Session(region_name='eu-central-1')
ec2 = aws_session.resource('ec2')

instances = []

tokens = []

if os.environ['TOKEN1']:
    tokens.append(os.environ['TOKEN1'])

@app.route('/databases', methods=['GET'])
def get_databases():
    headers = request.headers
    if not headers.get("X-AUTH"):
        abort(400)
    auth = headers.get("X-AUTH")
    validate_token(auth)
    return json.dumps(instances)

@app.route('/databases', methods=['POST'])
def create_database():
    headers = request.headers
    new_instance = {}
    if not headers.get("X-AUTH") or not request.json or ( not 'name' in request.json and not 'plan' in request.json ):
        abort(400)
    auth = headers.get("X-AUTH")
    validate_token(auth)    
    instance = aws_create_instance(request.json['name'],request.json['plan']) # CREATE EC2 Instance
    new_instance['Plan'] = request.json['plan']
    new_instance['Name'] = request.json['name']
    new_instance['Id'] = instance[0].id
    instances.append(new_instance)
    return "database %s created with instance_type %s" % (request.json['name'], request.json['plan'])

@app.route('/databases/<id>', methods=['DELETE'])
def delete_database(id):
    global instances
    headers = request.headers
    if not headers.get("X-AUTH"):
        abort(400)
    auth = headers.get("X-AUTH")
    validate_token(auth)
    aws_delete_instance(id)
    instances = [i for i in instances if not (i['Id'] == id)]
    return "database %s deleted!" % id


def aws_create_instance(name, instance_type):
    user_data = '''#!/bin/bash
            apt-get update
            apt-get install wget
            export PUBLIC_IP=`curl ifconfig.co`
            export RELEASE="3.3.13"
            wget https://github.com/etcd-io/etcd/releases/download/v${RELEASE}/etcd-v${RELEASE}-linux-amd64.tar.gz
            tar xvf etcd-v${RELEASE}-linux-amd64.tar.gz
            cd etcd-v${RELEASE}-linux-amd64
            sudo mv etcd etcdctl /usr/local/bin 
            sudo mkdir -p /var/lib/etcd/
            sudo mkdir /etc/etcd
            sudo groupadd --system etcd
            sudo useradd -s /sbin/nologin --system -g etcd etcd 
            sudo chown -R etcd:etcd /var/lib/etcd/ 
            etcd --listen-client-urls "http://0.0.0.0:2379" --advertise-client-urls "http://${PUBLIC_IP}:2379"
            '''

    instance = ec2.create_instances(
                                    ImageId='ami-0ac05733838eabc06',
                                    InstanceType=instance_type,
                                    MaxCount=1,
                                    MinCount=1,
                                    UserData=user_data,
                                    KeyName='devops',
                                    TagSpecifications=[
                                        {
                                            'ResourceType': 'instance',
                                            'Tags': [
                                                {
                                                    'Key': 'Name',
                                                    'Value': name
                                                },
                                            ]
                                        }
                                    ]
    )
    return instance

def aws_delete_instance(id):
    try:
        instance = ec2.instances.filter(InstanceIds = [id])
        instance.terminate()
    except ClientError:
        abort(404,'Instance ID %s not found' % id)

def validate_token(token):
    global tokens
    if token not in tokens:
        abort(401, {'message': 'Token is not valid'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)





