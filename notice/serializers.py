from rest_framework import serializers
from .models import Notice
from accounts.serializers import UserInfoSerializer

class NoticeSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True) # 유저 정보를 가져온다 !

    class Meta:
        model = Notice
        fields = '__all__'