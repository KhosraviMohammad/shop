from django.contrib import admin
from BaseUser.models import User


# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass