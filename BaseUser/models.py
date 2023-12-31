import uuid
import os
import re
import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _


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

    this has two fields create_date, update_date and is an abstract model which other models
    can inherit from it to have this field by default


    the purpose of it is to set log time


    """
    create_date = models.DateTimeField(auto_now_add=True, verbose_name=_('created date'))
    update_date = models.DateTimeField(auto_now=True, verbose_name=_('update date'))

    class Meta:
        abstract = True
        ordering = ['create_date']

    def update_field_model_obj(self, valid_data: dict) -> None:
        '''
        it finds all keys from valid_data that match with the fields which comes form the model that inherits
        form this model and set their value

        :param valid_data: dict
        :return: None
        '''

        for key, value in valid_data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BaseUserFieldModel(BaseFieldsModel):
    '''
    this has two fields created_by, updated_by and is an abstract model which other models
    can inherit from it to have this field by default

    the purpose of it is to log who is creating and updating

    it inherits from BaseFieldsModel is meant to have create_date, update_date fields by default

    '''

    created_by = models.ForeignKey('BaseUser.User', on_delete=models.DO_NOTHING, blank=True, null=True,
                                   verbose_name=_('created by'), related_name='created_%(class)ss')
    updated_by = models.ForeignKey('BaseUser.User', on_delete=models.DO_NOTHING, blank=True, null=True,
                                   verbose_name=_('updated by'), related_name='updated_%(class)ss')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        '''
        at first time, it sets passed user to created_by and updated_by fields if pk is None
        at other times, it sets passed user to updated_by fields if pk is not None

        :param args:
        :param kwargs: {user:user}
        :return:
        '''
        self.posted_user = kwargs.pop('user', None)
        if self.posted_user and not self.posted_user.is_anonymous:
            if self.pk is None:
                self.created_by = self.posted_user
            self.updated_by = self.posted_user
        super(BaseFieldsModel, self).save(*args, **kwargs)


class CustomUserManager(UserManager):
    '''
    custom manager for User model
    '''

    def create_user(self, email=None, password=None, **extra_fields):
        '''
        it takes all user field value from extra_fields and sets username with given mobile_number

        :param email:
        :param password:
        :param extra_fields:
        :return:
        '''
        username = extra_fields.get('mobile_number')
        user = super(CustomUserManager, self).create_user(username, email=email, password=password, **extra_fields)
        return user


class User(AbstractBaseUser, BaseFieldsModel, PermissionsMixin):
    """
    custom user model
    """
    GENDER_SELECT = (
        ('female', _('female')),
        ('male', _('male')),
    )
    username = models.CharField(max_length=150, unique=True, verbose_name=_('username'))
    first_name = models.CharField(verbose_name=_('first name'), max_length=30)
    gender = models.CharField(choices=GENDER_SELECT, verbose_name=_('gender'), max_length=20)
    last_name = models.CharField(verbose_name=_('last name'), max_length=30)
    mobile_number = models.CharField(max_length=11, unique=True,
                                     validators=[RegexValidator(re.compile(r'^[0-9]{11}$'))],
                                     verbose_name=_('mobile number'),
                                     help_text=_('Eleven digits without dash. Example: 09121328462'))
    avatar = models.ImageField(upload_to=avatar_directory_path, verbose_name=_('avatar'), blank=True, null=True)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    is_staff = models.BooleanField(verbose_name=_('is staff'), default=False)
    is_superuser = models.BooleanField(verbose_name=_('is superuser'), default=False)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __init__(self, *args, **kwargs):
        '''
        it sets username field with mobile_number field

        :param args:
        :param kwargs:
        '''
        kwargs.pop('email', None)
        super(User, self).__init__(*args, **kwargs)
        self.username = self.mobile_number

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

