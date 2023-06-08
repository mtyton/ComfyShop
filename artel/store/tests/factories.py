from factory import (
    Faker,
    SubFactory
)
from factory.django import (
    FileField,
    DjangoModelFactory
)


class CustomerDataFactory(DjangoModelFactory):
    class Meta:
        model = 'store.CustomerData'

    name = Faker('name')
    surname = Faker('name')
    email = Faker('email')
    phone = Faker('phone_number')
    street = Faker('street_address')
    city = Faker('city')
    zip_code = Faker('postcode')
    country = Faker('country')


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = 'store.Order'

    customer = SubFactory(CustomerDataFactory)
    created_at = Faker('date_time')
    updated_at = Faker('date_time')
    sent = Faker('boolean')


class DocumentTemplateFactory(DjangoModelFactory):
    class Meta:
        model = 'store.DocumentTemplate'

    name = Faker('name')
    file = FileField(filename="doc.odt")
    doc_type = "AGREEMENT"
