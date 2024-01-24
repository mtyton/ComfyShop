from factory import Faker
from factory.django import DjangoModelFactory


class MailTemplateFactory(DjangoModelFactory):
    class Meta:
        model = "mailings.MailTemplate"

    template_name = Faker("name")
    template = Faker("file_name", extension="html")
