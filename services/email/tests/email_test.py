import datetime
from unittest import TestCase

import jwt
from fastapi.testclient import TestClient

from config import SECRET_KEY
from main import app
from views import ALGORITHM


class EmailTestCase(TestCase):

    def setUp(self) -> None:
        self.data = {
            'recipient': 'test@example.com',
            'subject': 'Register account',
            'template': 'register.html',
            'data': {
                'username': 'test',
            },
            'user_id': 1,
        }
        self.client = TestClient(app)

    def test_email_send(self):
        self.data['token'] = jwt.encode(
            {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1), 'sub': 'access', 'user_id': 1},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        response = self.client.post('/send', json=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'msg': 'Email has been send'})

    def test_template_not_found(self):
        self.data['token'] = jwt.encode(
            {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1), 'sub': 'access', 'user_id': 1},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        self.data['template'] = 'test.html'
        response = self.client.post('/send', json=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Template not found'})

    def test_views_bad_token(self):
        self.data['user_id'] = 3
        self.data['token'] = jwt.encode(
            {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1), 'sub': 'access', 'user_id': 1},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        response = self.client.post('/send', json=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Bad token'})

    def test_bad_token(self):
        self.data['token'] = jwt.encode(
            {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1), 'sub': 'refresh', 'user_id': 1},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        response = self.client.post('/send', json=self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Bad token'})

    def test_token_lifetime_ended(self):
        self.data['token'] = jwt.encode(
            {'exp': datetime.datetime.utcnow() - datetime.timedelta(minutes=1), 'sub': 'access', 'user_id': 1},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        response = self.client.post('/send', json=self.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Token lifetime ended'})

    def test_jwt_error(self):
        self.data['token'] = jwt.encode(
            {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1), 'sub': 'access', 'user_id': 1},
            SECRET_KEY,
            algorithm=ALGORITHM
        ) + 'Z'
        response = self.client.post('/send', json=self.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'Could not validate credentials'})
