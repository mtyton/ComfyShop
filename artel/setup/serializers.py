from rest_framework import serializers

from setup.models import ComfyConfig


class ConfigSerializers(serializers.ModelSerializer):
    class Meta:
        model = ComfyConfig
        fields = [
            'logo', 'navbar_position', 'shop_enabled'
        ]
