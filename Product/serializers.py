from django.db import transaction

from rest_framework import serializers

from Product import models as product_models


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = product_models.Product
        fields = [
            'id', 'url', 'name', 'image', 'price', 'is_available',
        ]

