from django.test import TestCase
from django.urls import reverse

from store.tests import factories
from store import models as store_models


# TODO - this is fine for now, but we'll want to use factoryboy for this:
# https://factoryboy.readthedocs.io/en/stable/
# TODO - test have to rewritten - I'll do it tommorow

class OrderDocumentTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.order = factories.OrderFactory()
        self.document_template = factories.DocumentTemplateFactory(file__data="test")
    
    def test_generate_document_success(self):
        order_doc = store_models.OrderDocument.objects.create(
            order=self.order,
            template=self.document_template
        )
        document = order_doc.document
        self.assertIsInstance(document, bytes)
    
    def test_get_document_context_success(self):
        order_doc = store_models.OrderDocument.objects.create(
            order=self.order,
            template=self.document_template
        )
        context = order_doc.get_document_context()
        self.assertIsInstance(context, store_models.Context)
        self.assertEqual(context["order"].id, self.order.id)
        self.assertEqual(context["customer"].id, self.order.customer.id)
        self.assertEqual(context["products"].count(), 0)

    def test_send_order_document_mail_success(self):
        ...

    def test_send_order_document_mail_failure_wrong_email(self):
        ...
