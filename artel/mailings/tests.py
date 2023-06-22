from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from mailings.models import (
    MailTemplate,
    OutgoingEmail,
)


class TestMailTemplate(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.mail_template = MailTemplate.objects.create(
            template_name="test_template",
            template=SimpleUploadedFile(
                "test_template.html", b"<html>{{test_var}}</html>"
            ),
            subject="Test subject",
        )

    def test_load_and_process_template_success(self):
        content = self.mail_template.load_and_process_template({"test_var": "test"})
        self.assertEqual(content, "<html>test</html>")

    def test_load_and_process_template_missing_var_failure(self):
        content = self.mail_template.load_and_process_template({})
        self.assertEqual(content, "<html></html>")

    def test_load_and_preprocess_template_no_template_file(self):
        self.mail_template.template.delete()
        self.mail_template.template = None
        self.mail_template.save()
        with self.assertRaises(FileNotFoundError):
            self.mail_template.load_and_process_template({})


class TestOutgoingEmail(TestCase):
    
    def setUp(self) -> None:
        super().setUp()
        self.mail_template = MailTemplate.objects.create(
            template_name="test_template",
            template=SimpleUploadedFile(
                "test_template.html", b"<html>{{test_var}}</html>"
            ),
            subject="Test subject",
        )

    def test_send_success(self):
        mail = OutgoingEmail.objects.send(
            template_name="test_template",
            recipient="test@stardust.io", context={},
            sender="sklep-test@stardust.io"
        )
        self.assertEqual(mail.sent, True)
        # TODO outbox

    def test_send_missing_template_failure(self):
        with self.assertRaises(MailTemplate.DoesNotExist):
            OutgoingEmail.objects.send(
                template_name="missing_template",
                recipient="", sender="", context={}\
            )
