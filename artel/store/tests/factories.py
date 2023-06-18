from factory import (
    Faker,
    SubFactory,
    Factory
)
from factory.django import (
    FileField,
    DjangoModelFactory,
)


class ProductAuthorFactory(DjangoModelFactory):
    class Meta:
        model = 'store.ProductAuthor'

    name = Faker('name')
    surname = Faker('name')
    email = Faker('email')
    phone = Faker('phone_number')
    street = Faker('street_address')
    city = Faker('city')
    zip_code = Faker('postcode')
    country = Faker('country')
    display_name = Faker('name')


class ProductCategoryFactory(DjangoModelFactory):
    class Meta:
        model = 'store.ProductCategory'

    name = Faker('name')


class ProductCategoryParamFactory(DjangoModelFactory):
    class Meta:
        model = 'store.ProductCategoryParam'

    key = Faker('name')
    category = SubFactory(ProductCategoryFactory)
    param_type = 'str'


class ProductTemplateFactory(DjangoModelFactory):
    class Meta:
        model = 'store.ProductTemplate'

    title = Faker('name')
    description = Faker('text')
    code = Faker('name')
    author = SubFactory(ProductAuthorFactory)
    category = SubFactory(ProductCategoryFactory)


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = 'store.Product'

    name = Faker('name')
    info = Faker('text')
    price = Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    available = Faker('boolean')
    template = SubFactory(ProductTemplateFactory)


class PaymentMethodFactory(DjangoModelFactory):
    class Meta:
        model = 'store.PaymentMethod'

    name = Faker('name')
    description = Faker('text')
    active = Faker('boolean')


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = 'store.Order'

    payment_method = SubFactory(PaymentMethodFactory)
    created_at = Faker('date_time')
    updated_at = Faker('date_time')
    sent = Faker('boolean')


class DocumentTemplateFactory(DjangoModelFactory):
    class Meta:
        model = 'store.DocumentTemplate'

    name = Faker('name')
    file = FileField(filename="doc.odt")
    doc_type = "agreement"
