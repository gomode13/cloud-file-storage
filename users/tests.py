from test_plus.test import APITestCase


# Create your tests here.

class UserAuthAPITests(APITestCase):
    def setUp(self):
        self.user1 = self.make_user('testuser1', 'passnbalove1488')

    def test_sign_up(self):
        self.post('sign_up', data={'username': 'testuser2', 'password': 'passnbalove1488'})
        self.response_201()
        self.assertEqual(self.last_response.data, {"username": "testuser2"})

    def test_sign_up_duplicate_username(self):
        self.post('sign_up', data={'username': self.user1.username, 'password': 'passnbalove1488'})
        self.response_409()

    def test_sign_up_invalid_data(self):
        self.post('sign_up', data={'username': 'testuser2', 'password': 'asd12'})
        self.response_400()

    def test_sign_in(self):
        self.post('sign_in', data={'username': self.user1.username, 'password': 'passnbalove1488'})
        self.response_200()
        self.assertEqual(self.last_response.data, {"username": self.user1.username})

    def test_sign_in_invalid_username(self):
        self.post('sign_in', data={'username': 'tess', 'password': 'passnbalove1488'})
        self.response_400()

    def test_sign_in_invalid_password(self):
        self.post('sign_in', data={'username': self.user1.username, 'password': 'passnbalove1703'})
        self.response_401()

    def test_sign_in_user_not_exist(self):
        self.post('sign_in', data={'username': 'testuser2', 'password': 'passnbalove1488'})
        self.response_401()

    def test_sign_out(self):
        with self.login(username=self.user1.username, password='passnbalove1488'):
            self.post('sign_out', data={'username': self.user1.username})
        self.response_204()

    def test_sign_out_not_logged_in(self):
        self.post('sign_out', data={'username': self.user1.username})
        self.response_401()

    def test_current_user(self):
        with self.login(username=self.user1.username, password='passnbalove1488'):
            self.get('current_user')
        self.response_200()
        self.assertEqual(self.last_response.data, {"username": self.user1.username})

    def test_current_user_not_logged_in(self):
        self.get('current_user')
        self.response_401()