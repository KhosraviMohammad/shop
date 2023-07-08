from django.db import transaction

from rest_framework import serializers

from BaseUser.models import User


class UserRegisterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'gender', 'last_name', 'mobile_number', 'avatar', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        mobile_number = validated_data.pop('mobile_number')
        with transaction.atomic():
            user = User(username=mobile_number, mobile_number=mobile_number, **validated_data)
            user.set_password(password)
            user.save()
        return user
