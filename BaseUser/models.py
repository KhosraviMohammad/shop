import uuid
import os
import re
import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.core.validators import RegexValidator


# Create your models here.

def avatar_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    """
    مسیر ذخیره فایل آواتار
    :param instance: model instance
    :param filename: filename
    :return:
    """

    folder = instance.__class__.__name__
    file_url = os.path.join('user/profile/', '{folder}/{uuid}.{suffix}'.format(
        folder=folder, uuid=uuid.uuid4(),
        suffix=filename.split(".")[-1]), )
    return file_url


class BaseFieldsModel(models.Model):
    """

    مدل برای استفاده در همه مدل‌ها
    زمان ایجاد و بروزرسانی

    """
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    update_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ ویرایشی')

    class Meta:
        abstract = True
        ordering = ['create_date']

    def update_field_model_obj(self, valid_data):
        for key, value in valid_data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BaseUserFieldModel(BaseFieldsModel):
    created_by = models.ForeignKey('BaseUser.User', on_delete=models.DO_NOTHING, blank=True, null=True,
                                   verbose_name='سازنده', related_name='created_%(class)ss')
    updated_by = models.ForeignKey('BaseUser.User', on_delete=models.DO_NOTHING, blank=True, null=True,
                                   verbose_name='آخرین ویراستار', related_name='updated_%(class)ss')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.posted_user = kwargs.pop('user', None)
        if self.posted_user and not self.posted_user.is_anonymous:
            if self.pk is None:
                self.created_by = self.posted_user
            self.updated_by = self.posted_user
        super(BaseFieldsModel, self).save(*args, **kwargs)


class CustomUserManager(UserManager):
    pass


class User(AbstractBaseUser, BaseFieldsModel, PermissionsMixin):
    """
    مدل انتزاعی برای ایجاد کاربران جدید
    """
    GENDER_SELECT = (
        ('female', 'مونث'),
        ('male', 'مذکر'),
    )
    username = models.CharField(max_length=150, unique=True, verbose_name='نام کاربری')
    first_name = models.CharField(verbose_name='نام', max_length=30)
    gender = models.CharField(choices=GENDER_SELECT, verbose_name='جنسیت', max_length=20)
    last_name = models.CharField(verbose_name='نام خانوادگی', max_length=30)
    mobile_number = models.CharField(max_length=11, unique=True,
                                     validators=[RegexValidator(re.compile(r'^[0-9]{11}$'))],
                                     verbose_name='شماره همراه',
                                     help_text='یازده رقمی بدون خط تیره. نمونه: 09121328462')
    avatar = models.ImageField(upload_to=avatar_directory_path, blank=True, null=True)
    is_active = models.BooleanField(verbose_name='وضعیت', default=True)
    is_staff = models.BooleanField(verbose_name='وضعیت کارمندی', default=False)
    is_superuser = models.BooleanField(verbose_name='ابر کاربر', default=False)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)
