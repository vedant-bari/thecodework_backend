from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .permissions import IsUserOrReadOnly
from .serializers import UserSerializer
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib import messages
from django.http import HttpResponseRedirect

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


# class UserCreateViewSet(mixins.CreateModelMixin,
#                         viewsets.GenericViewSet):
#     """
#     Creates user accounts
#     """
#     queryset = User.objects.all()
#     serializer_class = CreateUserSerializer
#     permission_classes = (AllowAny,)


class UserVerificationCodeView(generics.ListAPIView):
    # queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        # queryset = self.get_queryset().filter()
        print("token", request.META.get('HTTP_AUTHORIZATION',None))
        query_params = request.query_params
        user = self.request.user
        print('user {} query_params {} user_code {}'.format(user,query_params.get('verfication_code'),user.verification_code))

        if user.verification_code == int(query_params.get('verfication_code')):
          print("in if")    
          serializer = UserSerializer(user)
          return Response(serializer.data)
        return Response({"message": "incorrect code"},status = status.HTTP_400_BAD_REQUEST)

