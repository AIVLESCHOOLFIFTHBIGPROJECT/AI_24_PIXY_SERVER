from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model

from accounts.serializers import UserSerializer, UserInfoSerializer
import json, os
from pathlib import Path
# 특정 이미지파일만 받기
WHITE_LIST_EXT = [
    '.jpg',
    '.jpeg',
    '.png'
]
# 회원가입
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    # 'json' 키에서 데이터 가져오기
    json_data = request.data.get('json')
    data = json.loads(json_data)
    
    # 이미지 파일 가져오기
    uploaded_file = request.FILES.get('business_r')
    if uploaded_file:
        # 파일 확장자 확인
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in WHITE_LIST_EXT:
            return Response({"detail": "Only .jpg and .jpeg and .png files are allowed."}, status=status.HTTP_400_BAD_REQUEST)
    data['business_r'] = uploaded_file
    serializer = UserSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        user.set_password(data['password'])
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 로그인
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    # 보안상의 이유로 아이디와 비밀번호를 통일해서 오류메시지 날림
    user = authenticate(email=email, password=password)
    if user is None:
        return Response({'message': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    update_last_login(None, user)

    return Response({'refresh_token': str(refresh),
                     'access_token': str(refresh.access_token)}, status=status.HTTP_200_OK)
# 로그아웃
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        # refresh토큰 blacklist에 추가
        refresh_token = request.data.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': '로그아웃 성공!!'}, status=status.HTTP_205_RESET_CONTENT)
    
    except Exception as e:
        return Response({'message': '로그아웃 실패!!'}, status=status.HTTP_400_BAD_REQUEST)
    
# 로그아웃(보류)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all(request):
    tokens = OutstandingToken.objects.filter(user_id=request.data.get('email'))
    for token in tokens:
        t, _ = BlacklistedToken.objects.get_or_create(token=token)

    return Response({'message': '로그아웃 성공!!'}, status=status.HTTP_205_RESET_CONTENT)

# 회원정보 조회, 회원정보 수정(의도하지 않은 토큰도 같이 생긴다. -> 조정필요)
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    # 회원정보 조회
    if request.method == 'GET':
        return Response(UserInfoSerializer(request.user).data, status=status.HTTP_200_OK)
    # 회원정보 수정
    elif request.method == 'PUT':
        # 'json' 키에서 데이터 가져오기
        json_data = request.data.get('json')
        data = json.loads(json_data)
        # 기존에 있던 이미지 조회
        old_image_path = request.user.business_r
        BASE_DIR = Path(__file__).resolve().parent.parent
        MEDIA_ROOT = os.path.join(BASE_DIR)
        # 기존 이미지 삭제
        if old_image_path and os.path.exists(MEDIA_ROOT+old_image_path.url):
            os.remove(MEDIA_ROOT+old_image_path.url)
        # 이미지 파일 가져오기
        uploaded_file = request.FILES.get('business_r')
        if uploaded_file:
            # 파일 확장자 확인
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if file_extension not in WHITE_LIST_EXT:
                return Response({"detail": "Only .jpg and .jpeg and .png files are allowed."}, status=status.HTTP_400_BAD_REQUEST)
        data['business_r'] = uploaded_file
        serializer = UserInfoSerializer(request.user, data=data, partial=True)
        if serializer.is_valid():
            # 기존에 있던 refresh_token은 blacklist에 넣자.
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            # 새로운 token을 발급받자
            refresh = RefreshToken.for_user(request.user)
            # Update
            serializer.save()
            return Response({'serializer':serializer.data , 'refresh_token': str(refresh), 'access_token': str(refresh.access_token)},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# 회원 탈퇴
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user = request.user
    try:
        # 사용자 탈퇴 로직 (예: 사용자 데이터 삭제)
        user.delete()
        # JWT 토큰 무효화
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            # 블랙리스트에 토큰이 이미 있는지 확인
            if not BlacklistedToken.objects.filter(token=token).exists():
                # 토큰을 블랙리스트에 추가
                BlacklistedToken.objects.create(token=token)
        return Response({'message': 'Account has been deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# 아이디 찾기
@api_view(['POST'])
@permission_classes([AllowAny])
def find_userid(request):
    target_email = request.data.get('email')
    User = get_user_model()
    user = User.objects.filter(email=target_email)
    print(user)
    if not user.exists():
        return Response({'message': '해당 아이디는 존재하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    data = {'email' : user.first().email}
    return Response(data, status=status.HTTP_200_OK)