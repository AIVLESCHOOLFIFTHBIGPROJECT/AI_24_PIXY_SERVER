from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

from accounts.serializers import UserSerializer
import json, os

WHITE_LIST_EXT = [
    '.jpg',
    '.jpeg',
    '.png'
]
# 동의여부 default할지 think
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    # 'json' 키에서 데이터 가져오기
    json_data = request.data.get('json')
    data = json.loads(json_data)
    
    # 이미지 파일 가져오기
    uploaded_file = request.FILES.get('bussiness_r')
    if uploaded_file:
        # 파일 확장자 확인
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in WHITE_LIST_EXT:
            return Response({"detail": "Only .jpg and .jpeg and .png files are allowed."}, status=status.HTTP_400_BAD_REQUEST)
    data['bussiness_r'] = uploaded_file
    serializer = UserSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        user.set_password(data['password'])
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    # 이후에 아이디,비밀번호 구분하기
    user = authenticate(email=email, password=password)
    if user is None:
        return Response({'message': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    update_last_login(None, user)

    return Response({'refresh_token': str(refresh),
                     'access_token': str(refresh.access_token), }, status=status.HTTP_200_OK)