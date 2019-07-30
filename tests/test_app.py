import unittest, os, json
os.environ["TOKEN1"] = "token123"
from api import app
from unittest.mock import Mock, MagicMock
import pdb

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.app
        self.client = self.app.test_client()
        self.headers = {'Content-Type': 'application/json', 'X-AUTH': 'token123'}
        self.data = {'name': 'instanceTest', 'plan': 't2.micro'}

    def test_use_invalid_token(self):
        headers = {'Content-Type': 'application/json', 'X-AUTH': 'wrongtoken123'}
        resp = self.client.get(path='/databases', headers=headers)
        self.assertEqual(resp.status_code, 401)

    def test_get_databases(self):
        resp = self.client.get(path='/databases', headers=self.headers)
        self.assertEqual(resp.status_code, 200)
    
    def test_get_400_without_header(self):
        headers = {'Content-Type': 'application/json'}
        resp = self.client.get(path='/databases', headers=headers)
        self.assertEqual(resp.status_code, 400)

    def test_create_new_database(self):
        testinstance = type('instance', (object,), 
                 {'id':'i-123456'})()
        app.ec2.create_instances = MagicMock(return_value=[testinstance])
        resp = self.client.post(path='/databases', headers=self.headers, data=json.dumps(self.data))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual('i-123456', app.instances[0]['Id'])
    
    def test_400_create_new_database(self):
        headers = {'Content-Type': 'application/json'}
        data1 = {'name': 'instanceTest'}
        data2 = {'plan': 't2.micro'}
        self.assertEqual(self.client.post(path='/databases', headers=headers, data=json.dumps(self.data)).status_code, 400)
        self.assertEqual(self.client.post(path='/databases', headers=self.headers, data=data1).status_code, 400)
        self.assertEqual(self.client.post(path='/databases', headers=self.headers, data=data2).status_code, 400)

    def test_delete_database(self):
        app.aws_delete_instance = MagicMock(return_value='ok')
        resp = self.client.delete(path='/databases/i-123457', headers=self.headers)
        self.assertEqual(resp.status_code, 200)

    def test_instance_terminate_called_on_delete(self):
        testinstance = type('instance', (object,), 
                 {'id':'i-123456'})()
        # app.ec2.instances.filter = Mock(return_value=testinstance)
        resp = self.client.delete(path='/databases/i-123456', headers=self.headers)
        self.assertEqual(resp.status_code, 200)