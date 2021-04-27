from rest_framework import serializers
from rest_framework import exceptions
import random
from .models import User
from .util import send_otp_mail


from allauth.account import app_settings as allauth_settings
from allauth.utils import email_address_exists
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email



from rest_framework import serializers
from .models import User
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.utils import import_callable
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import authenticate 
from django.conf import settings
# from django.contrib.auth import get_user_model
# UserModel = get_user_model()



def randomDigits(digits):
    lower = 10**(digits-1)
    upper = 10**digits - 1
    return random.randint(lower, upper)
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name',)
        read_only_fields = ('username', )


class CreateUserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token',)
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}


class LoginSerializer(serializers.ModelSerializer):
    """Login Serialization for first_token"""
    email = serializers.EmailField(write_only=True)
    password  = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def _validate_user(self, email, password):
        user = None
        print("I am here")
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
              raise exceptions.AuthenticationFailed('No such user') 
            else:
                
                user.verification_code = randomDigits(6)
                print("random_code", user.verification_code)
                user.save()  
                send_otp_mail(user)

        else:
            raise exceptions.ValidationError('email/password mismatch')
        return user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = self._validate_user(email, password)
        attrs['user'] = user
        return attrs


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match."))
        return data

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = User
        fields = ()


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """
        Required to allow using custom USER_DETAILS_SERIALIZER in
        JWTSerializer. Defining it here to avoid circular imports
        """
        rest_auth_serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})
        JWTUserDetailsSerializer = import_callable(
            rest_auth_serializers.get('USER_DETAILS_SERIALIZER', UserDetailsSerializer)
        )
        user_data = JWTUserDetailsSerializer(obj['user'], context=self.context).data
        return user_data        