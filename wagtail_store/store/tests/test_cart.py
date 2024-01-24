from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase

from store.tests import factories
from wagtail_store.tests import BaseComfyTestCaseMixin


class SessionCartTestCase(BaseComfyTestCaseMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.product = factories.ProductFactory(price=100)
        self.second_product = factories.ProductFactory(price=200)

    def test_add_item_simple_success(self):
        self.client.post(
            reverse("cart-action-add-product"),
            {"product_id": self.product.id, "quantity": 1},
        )
        self.assertEqual(
            self.client.session[settings.CART_SESSION_ID][str(self.product.author.id)][str(self.product.id)], 1
        )

    def test_add_item_complex_success(self):
        self.client.post(
            reverse("cart-action-add-product"),
            {"product_id": self.product.id, "quantity": 1},
        )
        self.assertEqual(
            self.client.session[settings.CART_SESSION_ID][str(self.product.author.id)][str(self.product.id)], 1
        )
        self.client.post(
            reverse("cart-action-add-product"),
            {"product_id": self.product.id, "quantity": 1},
        )
        self.assertEqual(
            self.client.session[settings.CART_SESSION_ID][str(self.product.author.id)][str(self.product.id)], 2
        )
        self.client.post(
            reverse("cart-action-add-product"),
            {"product_id": self.second_product.id, "quantity": 5},
        )
        final_dict = {
            str(self.product.author.id): {
                str(self.product.id): 2,
            }
        }
        final_dict.update(
            {
                str(self.second_product.author.id): {
                    str(self.second_product.id): 5,
                }
            }
        )
        self.assertDictEqual(self.client.session[settings.CART_SESSION_ID], final_dict)

    def test_add_item_invalid_product_id(self):
        response = self.client.post(
            reverse("cart-action-add-product"),
            {"product_id": 999, "quantity": 1},
        )
        self.assertEqual(response.status_code, 400)

    def test_add_item_invalid_quantity(self):
        response = self.client.post(
            reverse("cart-action-add-product"),
            {"product_id": self.product.id, "quantity": "invalid"},
        )
        self.assertEqual(response.status_code, 400)

    def test_remove_item_success(self):
        self.client.post(
            reverse("cart-action-add-product"),
            {"product_id": self.product.id, "quantity": 1},
        )
        self.assertEqual(
            self.client.session[settings.CART_SESSION_ID][str(self.product.author.id)][str(self.product.id)], 1
        )
        self.client.post(
            reverse("cart-action-remove-product"),
            {"product_id": self.product.id},
        )
        self.assertEqual(self.client.session[settings.CART_SESSION_ID], {str(self.product.author.id): {}})

    def test_remove_item_invalid_product_id(self):
        response = self.client.post(
            reverse("cart-action-remove-product"),
            {"product_id": 999},
        )
        self.assertEqual(response.status_code, 400)

    def test_update_item_quantity_success(self):
        self.client.post(
            reverse("cart-action-add-product"),
            {"product_id": self.product.id, "quantity": 1},
        )
        self.assertEqual(
            self.client.session[settings.CART_SESSION_ID][str(self.product.author.id)][str(self.product.id)], 1
        )
        self.client.put(
            reverse("cart-action-update-product", kwargs={"pk": self.product.id}),
            {"quantity": 5},
        )
        self.assertEqual(
            self.client.session[settings.CART_SESSION_ID][str(self.product.author.id)][str(self.product.id)], 5
        )

    def test_update_item_quantity_invalid_product_id(self):
        response = self.client.put(f'en/{reverse("cart-action-update-product", kwargs={"pk": 2137})}', {"quantity": 5})
        self.assertEqual(response.status_code, 404)
