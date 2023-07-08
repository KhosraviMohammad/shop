from django.core.management.base import BaseCommand

from BaseUser.models import User
from generic import funcs as generic_funcs


class Command(BaseCommand):
    help = 'creating super user'

    # def add_arguments(self, parser):
    #
    #     # Optional argument

    def handle(self, *args, **kwargs):
        first_name = input('first name: ')
        last_name = input('last name: ')
        password = input('password: ')
        mobile_number = input('mobile number: ')

        admin_user = User(gender='male', first_name=first_name, last_name=last_name, mobile_number=mobile_number, is_active=True,
             is_staff=True, is_superuser=True,
             )
        admin_user.set_password(password)
        admin_user.save()
