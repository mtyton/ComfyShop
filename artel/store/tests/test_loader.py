import pandas as pd
from django.test import TestCase
from unittest.mock import patch

from store.tests import factories
from store.loader import ProductLoader


class TestProductLoader(TestCase):
    def setUp(self) -> None:
        self.category = factories.ProductCategoryFactory()
        self.template = factories.ProductTemplateFactory(category=self.category)
        self.category_params = [factories.ProductCategoryParamFactory(category=self.category) for _ in range(3)]
        self.category_param_values = [factories.ProductCategoryParamValueFactory(param=param) for param in self.category_params]
    
    def test_load_products_single_product_success(self):
        fake_df = pd.DataFrame({
            "template": [self.template.code],
            "price": [10.0],
            "name": ["Test product"],
            "available": [True],
            "params": [[
                (self.category_params[0].key, self.category_param_values[0].value), 
                (self.category_params[1].key, self.category_param_values[1].value),
                (self.category_params[2].key, self.category_param_values[2].value),
            ]]
        })
        with patch("store.loader.BaseLoader.load_data", return_value=fake_df):
            loader = ProductLoader("fake_path")
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
            "params": [[
                (self.category_params[0].key, self.category_param_values[0].value), 
                (self.category_params[1].key, self.category_param_values[1].value),
                (self.category_params[2].key, self.category_param_values[2].value),
            ]]
        })
        with patch("store.loader.BaseLoader.load_data", return_value=fake_df):
            loader = ProductLoader("fake_path")
            loader.process()

        self.assertEqual(self.template.products.count(), 0)
        mock_logger.exception.assert_called_with("could not convert string to float: 'FASDSADQAW'")

    @patch("store.loader.logger")
    def test_load_no_existing_template_code_failure(self, mock_logger):
        fake_df = pd.DataFrame({
            "template": ["NOTEEXISTINGTEMPLATE"],
            "price": [10.0],
            "name": ["Test product"],
            "available": [True],
            "params": [[
                (self.category_params[0].key, self.category_param_values[0].value), 
                (self.category_params[1].key, self.category_param_values[1].value),
                (self.category_params[2].key, self.category_param_values[2].value),
            ]]
        })
        with patch("store.loader.BaseLoader.load_data", return_value=fake_df):
            loader = ProductLoader("fake_path")
            loader.process()
        
        self.assertEqual(self.template.products.count(), 0)
        mock_logger.exception.assert_called_with("ProductTemplate matching query does not exist.")

    @patch("store.loader.logger")
    def test_not_existing_params_key_value_pairs_failure(self, mock_logger):
        fake_df = pd.DataFrame({
            "template": [self.template.code],
            "price": [10.0],
            "name": ["Test product"],
            "available": [True],
            "params": [[
                (self.category_params[0].key, self.category_param_values[2].value), 
                (self.category_params[1].key, self.category_param_values[0].value),
                (self.category_params[2].key, self.category_param_values[1].value),
            ]]
        })
        with patch("store.loader.BaseLoader.load_data", return_value=fake_df):
            loader = ProductLoader("fake_path")
            loader.process()
        
        self.assertEqual(self.template.products.count(), 0)
        mock_logger.exception.assert_called_with("ProductCategoryParamValue matching query does not exist.")
    