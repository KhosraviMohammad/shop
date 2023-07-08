from django.db import transaction

from rest_framework import serializers

from Product import models as product_models


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = product_models.Product
        fields = [
            'id', 'url', 'name', 'image', 'price', 'is_available', 'categories'
        ]


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    product_id_set = serializers.SerializerMethodField()

    class Meta:
        model = product_models.Category
        fields = [
            'id', 'url', 'name', 'product_set', 'product_id_set'
        ]

    def get_product_id_set(self, obj):
        product_id_list = []
        for product_id in obj.product_set.values_list('id'):
            product_id_list.append(product_id[0])
        return product_id_list
