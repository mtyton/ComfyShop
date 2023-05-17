from django.test import TestCase
from django.urls import reverse
from store.models import ProductAuthor, ProductCategory, ProductTemplate, Product


class StoreTestCase(TestCase):
    def setUp(self):
        self.productid = 1
        self.author = ProductAuthor.objects.create(name='Test Author')
        self.category = ProductCategory.objects.create(name='Test Category')
        self.template = ProductTemplate.objects.create(category=self.category,
                                                       author=self.author,
                                                       title='Test title',
                                                       code='Test code',
                                                       description='Test description'
                                                       )
        self.product = Product.objects.create(template=self.template,
                                              price=10.99)
        self.cart_url = reverse('view_cart')

    def test_add_to_cart(self):
        response = self.client.post(reverse('add_to_cart',
                                            args=[self.productid]))
        self.assertEqual(response.status_code, 302)

    def test_remove_from_cart(self):
        response = self.client.post(reverse('remove_from_cart',
                                            args=[self.productid]))
        self.assertEqual(response.status_code, 302)

    def test_view_cart(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
