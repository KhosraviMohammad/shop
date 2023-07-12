import os

from django.db import models

from BaseUser import models as user_models
from django.utils.translation import gettext_lazy as _

# Create your models here.


def product_image_directory_path(instance, filename):
    filename, extension = os.path.splitext(filename)
    return f'products/{instance.name}/{instance.name}{extension}'


class Product(user_models.BaseUserFieldModel):
    name = models.CharField(max_length=150, verbose_name=_('name'))
    image = models.ImageField(upload_to=product_image_directory_path, blank=True, null=True, verbose_name=_('image'))
    price = models.IntegerField(default=0, blank=True, verbose_name=_('price'))
    is_available = models.BooleanField(default=False, blank=True, verbose_name=_('is available'))
    categories = models.ManyToManyField('Product.Category', blank=True, related_name='product_set', verbose_name=_('categories'))

    def __str__(self):
        return self.name


class Category(user_models.BaseUserFieldModel):
    name = models.CharField(max_length=150, unique=True, verbose_name=_('name'))

    def __str__(self):
        return self.name
