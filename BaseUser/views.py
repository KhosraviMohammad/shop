from rest_framework import generics
from rest_framework.response import Response

from BaseUser.serializers import BlockAccessTokenSerializer
from BaseUser.models import OutstandingAccessToken, BlackListedAccessToken


# Create your views here.

class AccessTokenBlockView(generics.GenericAPIView):
    serializer_class = BlockAccessTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'log out'}, status=200)
