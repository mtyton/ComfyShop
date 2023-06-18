from django.test import TestCase
from django.urls import reverse
from django.core import mail

from store.tests import factories
from store import models as store_models


# TODO - this is fine for now, but we'll want to use factoryboy for this:
# https://factoryboy.readthedocs.io/en/stable/
# TODO - test have to rewritten - I'll do it tommorow


class OrderProductTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.author = factories.ProductAuthorFactory()
        self.order = factories.OrderFactory()
        self.product = factories.ProductFactory(template__author=self.author, price=100)
        self.second_product = factories.ProductFactory(template__author=self.author, price=200)


    def test_create_from_cart_single_product_success(self):
        products = store_models.OrderProduct.objects.create_from_cart(
            items=[{"product": self.product, "quantity": 1}],
            order=self.order
        )
        self.assertEqual(products.count(), 1)

    def test_create_from_cart_multiple_products_success(self):
        products = store_models.OrderProduct.objects.create_from_cart(
            items=[
                {"product": self.product, "quantity": 1}, 
                {"product": self.second_product, "quantity": 1}
            ],
            order=self.order
        )
        self.assertEqual(products.count(), 2)

    def test_create_from_cart_wrong_quanitity_failure(self):
        products = store_models.OrderProduct.objects.create_from_cart(
            items=[{"product": self.product, "quantity": -123}],
            order=self.order
        )
        self.assertEqual(products.count(), 0)

    
    def test_create_from_cart_empty_data_failure(self):
        products = store_models.OrderProduct.objects.create_from_cart(
            items=[],
            order=self.order
        )
        self.assertEqual(products.count(), 0)


class OrderTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.author = factories.ProductAuthorFactory()
        self.second_author = factories.ProductAuthorFactory()
        self.customer_data = {
            "first_name": "Jan",
            "last_name": "Kowalski",
            "email": "jan.kowalski@tepewu.pl",
            "phone": "",
            "address": "",
            "postal_code": "",
            "city": "",
            "country": "",

        }
        self.payment_method = factories.PaymentMethodFactory()
        factories.DocumentTemplateFactory()
        factories.DocumentTemplateFactory(doc_type="receipt")

    def test_create_from_cart_success_single_author(self):
        product = factories.ProductFactory(template__author=self.author, price=100)
        cart_items = [{
            "author": self.author,
            "products": [{"product": product, "quantity": 1}]
        }]
        orders = store_models.Order.objects.create_from_cart(
            cart_items=cart_items,
            customer_data=self.customer_data,
            payment_method=self.payment_method
        )
        self.assertEqual(orders.count(), 1)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, f"Zamówienie {orders[0].order_number}")


    def test_create_from_cart_success_multpile_authors(self):
        product = factories.ProductFactory(template__author=self.second_author, price=100)
        cart_items = [
            {
                "author": self.author,
                "products": [{"product": product, "quantity": 1}]
            }, {
                "author": self.second_author,
                "products": [{"product": product, "quantity": 1}]
            }
        ]
        orders = store_models.Order.objects.create_from_cart(
            cart_items=cart_items,
            customer_data=self.customer_data,
            payment_method=self.payment_method
        )
        self.assertEqual(orders.count(), 2)
        self.assertEqual(len(mail.outbox), 4)
        self.assertEqual(mail.outbox[0].subject, f"Zamówienie {orders[0].order_number}")
        self.assertEqual(mail.outbox[2].subject, f"Zamówienie {orders[1].order_number}")
