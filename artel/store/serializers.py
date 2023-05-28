from rest_framework import serializers

from store.models import Product


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


class CartProductAddSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            self.product = Product.obejcts.get(id=value)
        except Product.objects.DoesNotExist:
            raise serializers.ValidationError("Unable to add not existing product")
        return value

    def save(self, cart):
        cart.add_item(self.product, self.validated_data["quantity"])
