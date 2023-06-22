from factory.django import DjangoModelFactory
from factory import Faker


class MailTemplateFactory(DjangoModelFactory):
    class Meta:
        model = "mailings.MailTemplate"

    template_name = Faker("name")
    template = Faker("file_name", extension="html")
