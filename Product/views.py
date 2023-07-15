from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from Product.models import (
    Product, Category
)
from Product.serializers import (
    ProductSerializer, CategorySerializer
)
from generic import classes as g_classes


# Create your views here.


class ProductView(viewsets.ModelViewSet):
    '''
    a view for Product crud
    '''

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [g_classes.IsAdminUserOrReadOnlyPermission]
    filterset_fields = ['id', 'name', 'categories']


class CategoryView(viewsets.ModelViewSet):
    '''
    a view for Category crud
    '''
    queryset = Category.objects.all().prefetch_related('product_set')
    serializer_class = CategorySerializer
    permission_classes = [g_classes.IsAdminUserOrReadOnlyPermission]
    filterset_fields = ['name']
