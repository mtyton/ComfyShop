from rest_framework import serializers

from store.models import Product, ProductAuthor


class TagSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["title", "description", "price", "available", "tags"]

    tags = TagSerializer(many=True)


class CartProductSerializer(serializers.Serializer):
    product = ProductSerializer()
    quantity = serializers.IntegerField()


class ProductAuthorSerializer(serializers.Serializer):
    class Meta:
        model = ProductAuthor
        fields = ["display_name"]


class CartSerializer(serializers.Serializer):
    author = ProductAuthorSerializer()
    products = CartProductSerializer(many=True)


class CartProductAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Unable to add not existing product")
        return value

    def save(self, cart):
        cart.add_item(self.validated_data["product_id"], self.validated_data["quantity"])
