from django.urls import path, include

from rest_framework import routers

from Product.views import ProductView

router = routers.SimpleRouter()

router.register('product', ProductView)

urlpatterns = [
    path('', include(router.urls))
]
