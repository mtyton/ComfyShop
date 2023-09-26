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


class ProductTemplateFactory(DjangoModelFactory):
    class Meta:
        model = 'store.ProductTemplate'

    title = Faker('name')
    description = Faker('text')
    code = Faker('name')
    author = SubFactory(ProductAuthorFactory)
    category = SubFactory(ProductCategoryFactory)


class ProductTemplateParamFactory(DjangoModelFactory):
    class Meta:
        model = 'store.ProductTemplateParam'

    key = Faker('name')
    template = SubFactory(ProductTemplateFactory)
    param_type = 'str'


class ProductTemplateParamValueFactory(DjangoModelFactory):
    class Meta:
        model = 'store.ProductTemplateParamValue'

    param = SubFactory(ProductTemplateParamFactory)
    value = Faker('name')


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = 'store.Product'

    name = Faker('name')
    price = Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    available = Faker('boolean')
    template = SubFactory(ProductTemplateFactory)


class ProductParamFactory(DjangoModelFactory):
    class Meta:
        model = 'store.ProductParam'
    
    product = SubFactory(ProductFactory)
    param = SubFactory(ProductTemplateParamValueFactory)


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
