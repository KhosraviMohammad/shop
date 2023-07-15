from django.contrib import admin
from Product.models import Category, Product


# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)
