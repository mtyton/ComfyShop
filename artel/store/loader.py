import logging
import requests
import pandas as pd

from django.core import files

from store.models import (
    ProductTemplate,
    ProductCategoryParamValue,
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
    
    def _get_images(self, row) -> list[files.ContentFile]:
        urls = row["images"]
        images = []
        for url in urls:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                data = response.raw
            file_name = url.split("/")[-1]
            image = files.ContentFile(data, name=file_name)
            images.append(image)
        return images

    def _process_row(self, row):
        template = ProductTemplate.objects.get(code=row["template"])
        price = float(row["price"])
        name = row["name"]
        available = bool(row["available"])
        params = []
        for param in row["params"]:
            key, value = param
            param = ProductCategoryParamValue.objects.get(param__key=key, value=value)
            params.append(param)
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
            try:
                product = self._process_row(row)
            except Exception as e:
                # catch any error and log it, GlitchTip will catch it
                logger.exception(str(e))
            else:
                products.append(product)
        logger.info(f"Loaded {len(products)} products")
