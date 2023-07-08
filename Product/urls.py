from django.urls import path, include

from rest_framework import routers

from Product.views import ProductView, CategoryView

router = routers.SimpleRouter()

router.register('product', ProductView)
router.register('category', CategoryView)

urlpatterns = [
    path('', include(router.urls))
]
