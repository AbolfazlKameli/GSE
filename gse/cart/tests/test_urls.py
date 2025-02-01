from django.urls import reverse, resolve
from rest_framework.test import APITestCase

from gse.cart.views import *


class EndpointsTest(APITestCase):
    def test_cart_retrieve_resolves_to_cart_retrieve_api(self):
        url = reverse('cart:cart_retrieve')
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func.view_class, CartRetrieveAPI)
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
        )

    def test_cart_create_resolves_to_cart_item_add_api(self):
        url = reverse('cart:cart_create')
        resolver = resolve(url)
        response = self.client.post(url)
        self.assertEqual(resolver.func.view_class, CartItemAddAPI)
        self.assertIn(
            response.status_code,
            [status.HTTP_201_CREATED, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
        )

    def test_cart_delete_resolves_to_cart_item_delete_api(self):
        url = reverse('cart:cart_delete', args=[20])
        resolver = resolve(url)
        response = self.client.delete(url)
        self.assertEqual(resolver.func.view_class, CartItemDeleteAPI)
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
        )
