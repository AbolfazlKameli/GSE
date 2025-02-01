from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APITestCase

from gse.cart.views import (
    CartRetrieveAPI,
    CartItemAddAPI
)


class CartRetrieveAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('cart:cart_retrieve')

    def test_url_resolves_to_retrieveapi(self):
        resolver = resolve(self.url)
        self.assertEqual(resolver.func.view_class, CartRetrieveAPI)

    def test_retrieveapi_response(self):
        response = self.client.get(self.url)
        self.assertIn(
            response.status_code,
            [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
        )


class CartItemAddAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('cart:cart_create')

    def test_url_resolves_to_addapi(self):
        resolver = resolve(self.url)
        self.assertEqual(resolver.func.view_class, CartItemAddAPI)

    def test_addapiresponse(self):
        response = self.client.post(self.url)
        self.assertIn(
            response.status_code,
            [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]
        )
