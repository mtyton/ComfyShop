import logging
import time
import requests
import pandas as pd

from django.core.files.base import ContentFile
from store.models import (
    ProductTemplate,
    ProductCategoryParamValue,
    ProductCategoryParam,
    Product, 
    ProductImage
)


logger = logging.getLogger(__name__)


class BaseLoader:
    def __init__(self, path):
        self.path = path

    def load_data(self):
        return pd.read_csv(self.path)


class TemplateLoader(BaseLoader):
    ...


class ProductLoader(BaseLoader):
    
    def _clear(self):
        Product.objects.all().delete()

    def __init__(self, path, param_names, clear=False):
        super().__init__(path)
        self.param_names = param_names
        if clear:
            self._clear()

    def _get_images(self, row) -> list[ContentFile]:
        url = row["images"]
        images = []
        response = requests.get(url+"/download", stream=True)
        print(response.status_code)
        if response.status_code == 200:
            data = response.content
            image = ContentFile(data, name=row["template"])
            images.append(image)
        return images

    def _process_row(self, row):
        template = ProductTemplate.objects.get(code=row["template"])
        price = float(row["price"].strip("zł").replace(",", "."))
        name = row["name"]
        available = bool(row["available"])
        params = []
        for key in self.param_names:
            value = row[key]
            param, _ = ProductCategoryParam.objects.get_or_create(key=key, category=template.category)
            param_value, _ = ProductCategoryParamValue.objects.get_or_create(param=param, value=value)
            params.append(param_value)
        product = Product.objects.get_or_create_by_params(template=template, params=params)
        product.price = price
        product.name = name
        product.available = available

        images = self._get_images(row)
        for i, image in enumerate(images):
            ProductImage.objects.create(product=product, image=image, is_main=bool(i==0))
        product.save()
        return product

    def process(self):
        data = self.load_data()
        products = []
        for _, row in data.iterrows():
            time.sleep(5)
            try:
                product = self._process_row(row)
            except Exception as e:
                # catch any error and log it, GlitchTip will catch it
                logger.exception(str(e))
            else:
                products.append(product)
        logger.info(f"Loaded {len(products)} products")
