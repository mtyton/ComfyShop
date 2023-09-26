
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.core.exceptions import ValidationError
from django.db import transaction

from store.tests import factories
from store import models as store_models
from mailings.tests.factories import MailTemplateFactory
from artel.tests import BaseComfyTestCaseMixin


class ProductCategoryParamTestCase(BaseComfyTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.category = factories.ProductCategoryFactory()
        self.template = factories.ProductTemplateFactory(category=self.category)
        self.param = factories.ProductTemplateParamFactory(
            template=self.template,
            param_type="int",
            key="test_param"
        )
    
    def test_get_available_values_no_values_success(self):
        available_values = [v for v in self.param.get_available_values()]
        self.assertEqual(available_values, [])

    def test_get_available_values_one_value_success(self):
        factories.ProductTemplateParamValueFactory(param=self.param, value="23")
        available_values = [v for v in self.param.get_available_values()]
        self.assertEqual(available_values, [23])
        self.assertEqual(len(available_values), 1)

    def test_get_available_values_multiple_values_success(self):
        factories.ProductTemplateParamValueFactory(param=self.param, value="23")
        factories.ProductTemplateParamValueFactory(param=self.param, value="24")
        factories.ProductTemplateParamValueFactory(param=self.param, value="25")
        available_values = [v for v in self.param.get_available_values()]
        self.assertEqual(available_values, [23, 24, 25])
        self.assertEqual(len(available_values), 3)


class ProductTemplateParamValueTestCase(BaseComfyTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.category = factories.ProductCategoryFactory()
        self.template = factories.ProductTemplateFactory(category=self.category)
    

    def test_get_value_success(self):
        param = factories.ProductTemplateParamFactory(
            template=self.template,
            param_type="int",
            key="test_param"
        )
        param_value = factories.ProductTemplateParamValueFactory(param=param, value="23")
        proper_value = param_value.get_value()
        self.assertEqual(proper_value, 23)
    
    def test_get_value_failure_wrong_value(self):
        param = factories.ProductTemplateParamFactory(
            template=self.template,
            param_type="int",
            key="test_param"
        )
        param_value = factories.ProductTemplateParamValueFactory(param=param, value="wrong_value")
        proper_value = param_value.get_value()
        self.assertEqual(proper_value, None)


class ProductTestCase(BaseComfyTestCaseMixin, TestCase):

    def test_template_params_one_value_success(self):
        product = factories.ProductFactory()
        param = factories.ProductTemplateParamFactory(
            template=product.template,
            param_type="int",
            key="test_param"
        )
        param_value = factories.ProductTemplateParamValueFactory(param=param, value="23")
        with transaction.atomic():
            product.params.add(param_value)
        product.save()
        self.assertEqual(product.params.count(), 1)
        self.assertEqual(product.params.first().get_value(), 23)

    def test_template_params_multiple_values_failure(self):
        product = factories.ProductFactory()
        param = factories.ProductTemplateParamFactory(
            template=product.template,
            param_type="int",
            key="test_param"
        )
        param_value = factories.ProductTemplateParamValueFactory(param=param, value="23")
        sec_param_value = factories.ProductTemplateParamValueFactory(param=param, value="24")
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                product.params.add(param_value)
                product.params.add(sec_param_value)
        self.assertEqual(product.params.count(), 0)

    def test_get_or_create_by_params_success(self):
        product = factories.ProductFactory(available=True)
        value1 = factories.ProductTemplateParamValueFactory()
        value2 = factories.ProductTemplateParamValueFactory()
        product.params.add(value1)
        product.params.add(value2)
        product.save()
        prod = store_models.Product.objects.get_or_create_by_params(
            params=[value1, value2], template=product.template,
        )
        self.assertIsNotNone(prod)
        self.assertEqual(prod.pk, product.pk)
        self.assertTrue(prod.available)

    def test_get_or_create_by_params_success_not_existing_product(self):
        product = factories.ProductFactory(available=True)
        value1 = factories.ProductTemplateParamValueFactory()
        value2 = factories.ProductTemplateParamValueFactory()
        product.params.add(value1)
        product.price = 13.0
        product.save()
        
        prod = store_models.Product.objects.get_or_create_by_params(
            params=[value1, value2], template=product.template,
        )
        self.assertIsNotNone(prod)
        self.assertNotEqual(prod.pk, product.pk)
        self.assertFalse(prod.available)
        self.assertEqual(prod.price, 0)

    def test_get_or_create_by_params_success_not_existing_product_no_other_products(self):
        template = factories.ProductTemplateFactory()
        value1 = factories.ProductTemplateParamValueFactory()
        value2 = factories.ProductTemplateParamValueFactory()
        
        prod = store_models.Product.objects.get_or_create_by_params(
            params=[value1, value2], template=template,
        )
        self.assertIsNotNone(prod)
        self.assertFalse(prod.available)
        self.assertEqual(prod.price, 0)


class OrderProductTestCase(BaseComfyTestCaseMixin, TestCase):
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


class OrderTestCase(BaseComfyTestCaseMixin, TestCase):
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
        MailTemplateFactory(template_name="order_created_user")
        MailTemplateFactory(template_name="order_created_author")

    @patch("mailings.models.MailTemplate.load_and_process_template", return_value="test")
    def test_create_from_cart_success_single_author(self, mocked_load):
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
        self.assertEqual(
            mail.outbox[0].subject, 
            f"Wygenerowano umowę numer {orders[0].order_number} z dnia {orders[0].created_at.strftime('%d.%m.%Y')}"
        )

    @patch("mailings.models.MailTemplate.load_and_process_template", return_value="test")
    def test_create_from_cart_success_multpile_authors(self, mocked_load):
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
        self.assertEqual(
            mail.outbox[0].subject, 
            f"Wygenerowano umowę numer {orders[0].order_number} z dnia {orders[0].created_at.strftime('%d.%m.%Y')}"
        )
        self.assertEqual(
            mail.outbox[2].subject, 
            f"Wygenerowano umowę numer {orders[1].order_number} z dnia {orders[1].created_at.strftime('%d.%m.%Y')}"
        )
