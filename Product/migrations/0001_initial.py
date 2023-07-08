# Generated by Django 4.2.3 on 2023-07-08 09:50

import Product.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='تاریخ ویرایشی')),
                ('name', models.CharField(max_length=150, verbose_name='نام محصول')),
                ('image', models.ImageField(blank=True, null=True, upload_to=Product.models.product_image_directory_path, verbose_name='تصویر')),
                ('price', models.IntegerField(blank=True, default=0, verbose_name='قیمت')),
                ('is_available', models.BooleanField(blank=True, default=False)),
            ],
            options={
                'ordering': ['create_date'],
                'abstract': False,
            },
        ),
    ]
