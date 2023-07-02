from django.test import TestCase
from django.core.exceptions import ValidationError

from store.tests import factories
from store.validators import ProductParamDuplicateValidator
from store.models import (
    ProductParam,
    Product
)


class CategoryParamValidationTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.product = factories.ProductFactory()

    def test_set_single_param_success(self):
        param = factories.ProductCategoryParamFactory(
            category=self.product.template.category,
            param_type="int",
            key="test_param"
        )
        param_value = factories.ProductCategoryParamValueFactory(param=param, value="23")
        param  = ProductParam(param_value=param_value)
        self.product.params.add(param_value)
        self.assertEqual(self.product.params.count(), 1)
        self.assertEqual(self.product.params.first().get_value(), 23)

    def test_set_multuiple_same_type_param_failure(self):
        param = factories.ProductCategoryParamFactory(
            category=self.product.template.category,
            param_type="int",
            key="test_param"
        )
        param_value = factories.ProductCategoryParamValueFactory(param=param, value="23")
        sec_param_value = factories.ProductCategoryParamValueFactory(param=param, value="24")
        param  = ProductParam(param_value=param_value)
        self.product.params.add(param_value)
        with self.assertRaises(ValidationError):
            self.product.params.add(sec_param_value)

