from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import update_last_login

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer, TokenObtainSerializer

from BaseUser.models import User, BlackListedAccessToken, OutstandingAccessToken
from generic.funcs import generate_state_full_jwt


class UserRegisterSerializer(serializers.HyperlinkedModelSerializer):
    '''
    UserRegisterSerializer for validating , creating, and updating new user
    '''

    class Meta:
        model = User
        fields = ['first_name', 'gender', 'last_name', 'mobile_number', 'avatar', 'password']

    def create(self, validated_data):
        '''
        create new user

        :param validated_data:
        :return:
        '''
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        '''
        it validates entered data and returns jwt token generated from generate_state_full_jwt

        :param attrs:
        :return:
        '''
        data = super().validate(attrs)

        state_full_jwt_token = generate_state_full_jwt(self.user)
        data.update(state_full_jwt_token)
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class BlockAccessTokenSerializer(serializers.Serializer):
    '''
    this serializer blocks given token when BlockAccessTokenSerializer.is_valid is involved
    '''

    access = serializers.CharField()

    def validate(self, attrs):
        '''
        fist it validates given access token and then blocks it

        if a token is in invalid, it raises ValidationError

        :param attrs:
        :return:
        '''

        # validate given data by super class
        data = super().validate(attrs)

        # takes access token
        raw_access_token = data.get('access')

        # following several lines check if a token is valid then blocks it otherwise raises ValidationError
        # two lines below checks the token is stored in OutstandingAccessToken else raises ValidationError
        outstanding_access_token_qu = OutstandingAccessToken.objects.filter(token=raw_access_token)
        if outstanding_access_token_qu.exists():
            # generating access token obj (rest_framework_simplejwt.tokens.AccessToken) from raw token
            access_token_obj = api_settings.AUTH_TOKEN_CLASSES[0](raw_access_token)
            user_id = access_token_obj.payload.get('user_id')
            # it checks the token is not in BlackListedAccessToken if it is not, it will block access toke
            # in BlackListedAccessToken else ValidationError
            if not BlackListedAccessToken.objects.filter(token=raw_access_token, user_id=user_id).exists():
                BlackListedAccessToken.objects.create(token=raw_access_token, user_id=user_id)
            else:
                raise serializers.ValidationError(_('token is not valid'))
        else:
            raise serializers.ValidationError(_('token is not valid'))

        return data
