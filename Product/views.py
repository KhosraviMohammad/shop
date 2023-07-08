from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from Product.models import (
    Product
)
from Product.serializers import (
    ProductSerializer
)
from generic import classes as g_classes


# Create your views here.


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [g_classes.IsAdminUserOrReadOnlyPermission]
