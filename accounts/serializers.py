from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'password', 'name', 'p_num', 'r_num', 'business_r','is_agreement1', 'is_agreement2', 'is_agreement3')

class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('name', 'p_num','r_num', 'business_r')

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.UUIDField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)
