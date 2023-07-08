import os

from django.db import models

from BaseUser import models as user_models


# Create your models here.


def product_image_directory_path(instance, filename):
    filename, extension = os.path.splitext(filename)
    return f'products/{instance.name}-{instance.id}/{instance.name}{extension}'


class Product(user_models.BaseFieldsModel):
    name = models.CharField(max_length=150, verbose_name='نام محصول')
    image = models.ImageField(upload_to=product_image_directory_path, blank=True, null=True, verbose_name='تصویر')
    price = models.IntegerField(default=0, blank=True, verbose_name='قیمت')
    is_available = models.BooleanField(default=False, blank=True, )
    categories = models.ManyToManyField('Product.Category', blank=True, related_name='product_set', verbose_name='دسته بندی')

    def __str__(self):
        return self.name


class Category(user_models.BaseFieldsModel):
    name = models.CharField(max_length=150, unique=True, verbose_name='نام')

    def __str__(self):
        return self.name
