from django.test import TestCase
from files import service
from django.core.files.uploadedfile import SimpleUploadedFile


# Create your tests here.

class FileServiceIntegrationTests(TestCase):
    def setUp(self):
        self.user1_id = 9998
        self.user2_id = 9999

    def tearDown(self):
        service.delete_folder(self.user1_id, '')
        service.delete_folder(self.user2_id, '')

    def test_upload_creates_file(self):
        file = SimpleUploadedFile('file.txt', b'hello')
        service.upload_file(self.user1_id, 'file.txt', file)
        self.assertTrue(service.resource_exists(self.user1_id, 'file.txt'))

    def test_delete_file(self):
        file = SimpleUploadedFile('file.txt', b'hello')
        service.upload_file(self.user1_id, 'file.txt', file)
        service.delete_file(self.user1_id, 'file.txt')
        self.assertFalse(service.resource_exists(self.user1_id, 'file.txt'))

    def test_move_relocates_file(self):
        file = SimpleUploadedFile('file.txt', b'hello')
        service.upload_file(self.user1_id, 'file.txt', file)
        service.move_resource(self.user1_id, 'file.txt', 'test-folder/file.txt')
        self.assertTrue(service.resource_exists(self.user1_id, 'test-folder/file.txt'))
        self.assertFalse(service.resource_exists(self.user1_id, 'file.txt'))

    def test_move_relocates_folder(self):
        file = SimpleUploadedFile('file.txt', b'hello')
        service.upload_file(self.user1_id, 'test-folder/file.txt', file)
        service.move_resource(self.user1_id, 'test-folder/', 'test-folder2/test-folder/')
        self.assertTrue(service.resource_exists(self.user1_id, 'test-folder2/test-folder/file.txt'))
        self.assertFalse(service.resource_exists(self.user1_id, 'test-folder/file.txt'))

    def test_user_cannot_access_others_files(self):
        file = SimpleUploadedFile('file.txt', b'hello')
        service.upload_file(self.user1_id, 'file.txt', file)
        self.assertTrue(service.resource_exists(self.user1_id, 'file.txt'))
        self.assertFalse(service.resource_exists(self.user2_id, 'file.txt'))

    def test_search_finds_only_own_files(self):
        file = SimpleUploadedFile('file.txt', b'hello')
        file_two = SimpleUploadedFile('file_two.txt', b'hello')
        service.upload_file(self.user1_id, 'file.txt', file)
        service.upload_file(self.user2_id, 'file_two.txt', file_two)
        result = service.search_resource(self.user1_id, 'file.txt')
        self.assertTrue(len(result) > 0)
        result = service.search_resource(self.user2_id, 'file_two.txt')
        self.assertTrue(len(result) > 0)
        result = service.search_resource(self.user1_id, 'file_two.txt')
        self.assertFalse(result)
        result = service.search_resource(self.user2_id, 'file.txt')
        self.assertFalse(result)
