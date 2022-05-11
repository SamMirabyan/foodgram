from django.test import Client, TestCase

from ..models import Tag


class TagsTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(
            name='test', color=22,
            slug='test'
        )
        self.client = Client()
        self.list_url = 'http://127.0.0.1:5000/api/tags/'
        self.retrieve_url = 'http://127.0.0.1:5000/api/tags/1/'

    def test_tags_list_endpoint_status_code(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_tags_retrieve_endpoint_status_code(self):
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, 200)

    def test_tags_list_endpoint_data(self):
        """
        Test if atributes of db tag instance equals to
        tag object atributes recieved from '/tags/' endpoint.
        """
        response = self.client.get(self.list_url)
        data = response.json()
        recieved_tag_object = data[0]
        payload = {'id': 1}
        payload.update(self.tag.__dict__)
        payload.pop('_state')
        self.assertEqual(len(data), 1)
        self.assertEqual(recieved_tag_object, payload)

    def test_tags_retrieve_endpoint_data(self):
        """
        Test if atributes of db tag instance equals to
        tag object atributes recieved from '/tags/1/' endpoint.
        """
        response = self.client.get(self.retrieve_url)
        tag_object = response.json()
        payload = {'id': 1}
        payload.update(self.tag.__dict__)
        payload.pop('_state')
        self.assertEqual(tag_object, payload)

    def test_create_new_tag(self):
        data = {
            'name': 'test',
            'color': 22,
            'slug': 'test'
        }
        request = self.client.post(self.list_url, data=data)
        print(dir(self.client))
        self.assertEquals(request.status_code, 401)

