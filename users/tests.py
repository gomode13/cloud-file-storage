from django.test import TestCase
from test_plus.test import APITestCase

from users.models import User


# Create your tests here.

class UserAuthAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', password='testusername1')
