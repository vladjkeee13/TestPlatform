
from django.test import TestCase, Client
from django.urls import reverse


class TestViewsDiagnostic(TestCase):

    fixtures = [
        'fixtures/users.json'
    ]

    def setUp(self):
        self.client = Client()

    def test_main_page(self):
        response = self.client.get(reverse('tests:home-page'))
        self.assertEqual(response.status_code, 200)

    def test_add_test(self):
        response = self.client.get(reverse('tests:add-test'))
        self.assertEqual(response.status_code, 302)

    def test_add_test_logged_in(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('tests:add-test'))
        self.assertEqual(response.status_code, 200)
