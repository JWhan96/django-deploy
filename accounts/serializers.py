from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import DefaultAccountAdapter
from dj_rest_auth.serializers import UserDetailsSerializer
from dj_rest_auth.serializers import PasswordChangeSerializer
from allauth.account.adapter import get_adapter
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(required=False, allow_blank=True, max_length=100)
    profile_image = serializers.ImageField(required=False)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'nickname': self.validated_data.get('nickname', ''),
            'profile_image': self.validated_data.get('profile_image', ''),
        }
    
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        user.save()
        self.custom_signup(request, user)
        # setup_user_email(request, user, [])
        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta:
        extra_fields = []
        # see https://github.com/iMerica/dj-rest-auth/issues/181
        # UserModel.XYZ causing attribute error while importing other
        # classes from `serializers.py`. So, we need to check whether the auth model has
        # the attribute or not
        if hasattr(UserModel, 'USERNAME_FIELD'):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, 'EMAIL_FIELD'):
            extra_fields.append(UserModel.EMAIL_FIELD)
        # if hasattr(UserModel, 'first_name'):
        #     extra_fields.append('first_name')
        # if hasattr(UserModel, 'last_name'):
        #     extra_fields.append('last_name')
        if hasattr(UserModel, 'nickname'):
            extra_fields.append('nickname')
        if hasattr(UserModel, 'profile_image'):
            extra_fields.append('profile_image')
        if hasattr(UserModel, 'like_rooms'):
            extra_fields.append('like_rooms')
        model = UserModel
        fields = ('pk', *extra_fields)
        read_only_fields = ('email',)
