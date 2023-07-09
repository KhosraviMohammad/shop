from django.db import transaction

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login

from BaseUser.models import User, BlackListedAccessToken, OutstandingAccessToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer, TokenObtainSerializer


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


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        outstanding_access_token = OutstandingAccessToken(token=data["access"], user=self.context.get('user'))
        outstanding_access_token.save()

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
