from django.test import TestCase
from django.shortcuts import reverse

from store.models import (
    ProductTemplateParam,
    ProductTemplateParamValue,
    TemplateParamValueChoices
)
from store.tests.factories import (
    ProductTemplateFactory,
    ProductCategoryFactory,
    ProductFactory,
    ProductTemplateParamValueFactory
)
from artel.tests import BaseComfyTestCaseMixin


class ConfigureProductViewTestCase(BaseComfyTestCaseMixin, TestCase):
    
    def setUp(self):
        super().setUp()
        self.category = ProductCategoryFactory()
        self.product_template = ProductTemplateFactory(category=self.category)
        # create template params and values for those params
        self.param1 = ProductTemplateParam.objects.create(
            key="Mocowanie", template=self.product_template,
            param_type=TemplateParamValueChoices.STRING
        )
        self.param1_value1 = ProductTemplateParamValueFactory(param=self.param1)
        self.param1_value2 = ProductTemplateParamValueFactory(param=self.param1)
        self.param2 = ProductTemplateParam.objects.create(
            key="Format", template=self.product_template,
            param_type=TemplateParamValueChoices.STRING
        )
        self.param2_value1 = ProductTemplateParamValueFactory(param=self.param2)
        self.param2_value2 = ProductTemplateParamValueFactory(param=self.param2)
        # create product variant
        self.variant1 = ProductFactory(
            template=self.product_template
        )
        self.variant1.params.set([self.param1_value1, self.param2_value1])
        self.variant1.save()

        self.variant2 = ProductFactory(
            template=self.product_template,
        )
        self.variant2.params.set([self.param1_value2, self.param2_value2])
        self.variant2.save()

    def test_get_success(self):
        response = self.client.get(
            reverse("product-configure", args=[self.product_template.pk]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/configure_product.html")

    def test_get_failure_wrong_pk(self):
        response = self.client.get(
            f'en/{reverse("product-configure", args=[12312])}',
        )
        self.assertEqual(response.status_code, 404)

    def test_post_success(self):
        data = {
            self.param1.key: [str(self.param1_value1.pk)],
            self.param2.key: [str(self.param2_value1.pk)]
        }
        response = self.client.post(
            reverse("product-configure", args=[self.product_template.pk]),
            data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("configure-product-summary", args=[self.variant1.pk]))

    def test_post_failure_not_existing_template(self):
        data = {
            self.param1.key: [str(self.param1_value1.pk)],
            self.param2.key: [str(self.param2_value1.pk)]
        }
        response = self.client.post(
            f"en/{reverse('product-configure', args=[123123])}",
            data=data
        )
        self.assertEqual(response.status_code, 404)

    def test_post_not_existing_config(self):
        data = {
            self.param1.key: [str(self.param1_value2.pk)],
            self.param2.key: [str(self.param2_value1.pk)]
        }
        response = self.client.post(
            reverse("product-configure", args=[self.product_template.pk]),
            data=data
        )
        self.assertEqual(response.status_code, 302)


class ConfigureProductSummaryViewTestCase(BaseComfyTestCaseMixin, TestCase):
    ...
