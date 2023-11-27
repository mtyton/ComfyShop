import pandas as pd
from django.test import TestCase
from unittest.mock import patch

from store.tests import factories
from store.loader import ProductLoader
from artel.tests import BaseComfyTestCaseMixin


class TestProductLoader(BaseComfyTestCaseMixin, TestCase):
    def setUp(self) -> None:
        self.category = factories.ProductCategoryFactory()
        self.template = factories.ProductTemplateFactory(category=self.category)
        self.template_params = [factories.ProductTemplateParamFactory(template=self.template) for _ in range(3)]
        self.templat_params_values = [factories.ProductTemplateParamValueFactory(param=param) for param in self.template_params]
    
    def test_load_products_single_product_success(self):
        fake_df = pd.DataFrame({
            "template": [self.template.code],
            "price": str(10.0),
            "name": ["Test product"],
            "available": [True],
            self.template_params[0].key: self.templat_params_values[0].value,
            self.template_params[1].key: self.templat_params_values[1].value,
            self.template_params[2].key: self.templat_params_values[2].value
        })
        with patch("store.loader.BaseLoader.load_data", return_value=fake_df):
            loader = ProductLoader("fake_path", [p.key for p in self.template_params])
            loader.process()

        self.assertEqual(self.template.products.count(), 1)
        product = self.template.products.first()
        self.assertEqual(product.price, 10.0)
        self.assertEqual(product.name, "Test product")
        self.assertEqual(product.available, True)

    @patch("store.loader.logger")
    def test_load_incorrect_data_types_failure(self, mock_logger):
        fake_df = pd.DataFrame({
            "template": [self.template.code],
            "price": ["FASDSADQAW"],
            "name": ["Test product"],
            "available": [True],
            self.template_params[0].key: self.templat_params_values[0].value,
            self.template_params[1].key: self.templat_params_values[1].value,
            self.template_params[2].key: self.templat_params_values[2].value
        })
        with patch("store.loader.BaseLoader.load_data", return_value=fake_df):
            loader = ProductLoader("fake_path", [p.key for p in self.template_params])
            loader.process()

        self.assertEqual(self.template.products.count(), 0)
        mock_logger.exception.assert_called_with("could not convert string to float: 'FASDSADQAW'")

    @patch("store.loader.logger")
    def test_load_no_existing_template_code_failure(self, mock_logger):
        fake_df = pd.DataFrame({
            "template": ["NOTEEXISTINGTEMPLATE"],
            "price": str(10.0),
            "name": ["Test product"],
            "available": [True],
            self.template_params[0].key: self.templat_params_values[0].value,
            self.template_params[1].key: self.templat_params_values[1].value,
            self.template_params[2].key: self.templat_params_values[2].value
        })
        with patch("store.loader.BaseLoader.load_data", return_value=fake_df):
            loader = ProductLoader("fake_path", [p.key for p in self.template_params])
            loader.process()
        
        self.assertEqual(self.template.products.count(), 0)
        mock_logger.exception.assert_called_with("ProductTemplate matching query does not exist.")
    