import os

from django.db import models

from BaseUser import models as user_models
from django.utils.translation import gettext_lazy as _

# Create your models here.


def product_image_directory_path(instance, filename):
    filename, extension = os.path.splitext(filename)
    return f'products/{instance.name}/{instance.name}{extension}'


class Product(user_models.BaseUserFieldModel):
    name = models.CharField(max_length=150, verbose_name=_('نام محصول'))
    image = models.ImageField(upload_to=product_image_directory_path, blank=True, null=True, verbose_name=_('تصویر'))
    price = models.IntegerField(default=0, blank=True, verbose_name=_('قیمت'))
    is_available = models.BooleanField(default=False, blank=True, )
    categories = models.ManyToManyField('Product.Category', blank=True, related_name='product_set', verbose_name=_('دسته بندی'))

    def __str__(self):
        return self.name


class Category(user_models.BaseUserFieldModel):
    name = models.CharField(max_length=150, unique=True, verbose_name=_('نام'))

    def __str__(self):
        return self.name
