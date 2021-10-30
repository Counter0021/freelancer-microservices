from unittest import TestCase, mock

from app.crud import message_crud
from tests import BaseTest, async_loop


class UpdateMessageTestCase(BaseTest, TestCase):

    def setUp(self) -> None:
        super().setUp()
        async_loop(message_crud.create(self.session, msg='Hello world!', sender_id=1, recipient_id=2))
        self.start_msg_text = 'Hello world!'

    def test_update_message(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)

        with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket:
                socket.send_json({'sender_id': 1, 'msg_id': 1, 'msg': 'Python', 'type': 'UPDATE'})
                self.assertEqual(
                    socket.receive_json(),
                    {'type': 'SUCCESS', 'data': {'msg': 'Message has been updated'}}
                )
                self.assertEqual(
                    socket.receive_json(),
                    {
                        'type': 'UPDATE_MESSAGE',
                        'data': {
                            'msg': 'Python',
                            'recipient_id': 2,
                            'id': 1,
                            'sender_id': 1,
                            'sender': {
                                'avatar': 'http://localhost:8000/media/test/lol.png',
                                'id': 1,
                                'username': 'test'
                            },
                            'created_at': f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(
                                ' ',
                                'T'
                            ),
                        }
                    }
                )

        self.assertEqual(async_loop(message_crud.get(self.session, id=1)).msg, 'Python')
        socket.close()

    def test_update_message_2_connection(self):
        self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
        created_at = f'{async_loop(message_crud.get(self.session, id=1)).created_at}Z'.replace(' ', 'T')

        with mock.patch('app.requests.sender_profile_request', return_value=self.user2) as _:
            with self.client.websocket_connect(f'{self.url}/ws/token') as socket_2:
                with mock.patch('app.requests.sender_profile_request', return_value=self.user) as _:
                    with self.client.websocket_connect(f'{self.url}/ws/token') as socket_1:
                        socket_1.send_json({'sender_id': 1, 'msg_id': 1, 'msg': 'Python', 'type': 'UPDATE'})
                        self.assertEqual(
                            socket_1.receive_json(),
                            {'type': 'SUCCESS', 'data': {'msg': 'Message has been updated'}}
                        )
                        self.assertEqual(
                            socket_1.receive_json(),
                            {
                                'type': 'UPDATE_MESSAGE',
                                'data': {
                                    'msg': 'Python',
                                    'recipient_id': 2,
                                    'id': 1,
                                    'sender_id': 1,
                                    'sender': {
                                        'avatar': 'http://localhost:8000/media/test/lol.png',
                                        'id': 1,
                                        'username': 'test'
                                    },
                                    'created_at': created_at,
                                }
                            }
                        )

                self.assertEqual(
                    socket_2.receive_json(),
                    {
                        'type': 'UPDATE_MESSAGE',
                        'data': {
                            'sender_id': 1, 'recipient_id': 2, 'msg': 'Python', 'id': 1, 'created_at': created_at,
                            'sender': self.user
                        }
                    }
                )

                self.assertEqual(len(async_loop(message_crud.all(self.session))), 1)
                socket_1.close()
                socket_2.close()
