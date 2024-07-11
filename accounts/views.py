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
from django.http import HttpResponse

# 구글 소셜로그인 변수 설정
state = os.environ.get("STATE")
BASE_URL = 'http://127.0.0.1:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'api/user/google/callback/'

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
    # 아이디와 비밀번호를 통일해서 오류 메시지를 날리는 것이 보안상 좋다.
    user = authenticate(email=email, password=password)
    if user is None:
        return Response({'message': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    response = Response({
        'message': '로그인 성공!!',
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    })
    # 쿠키 저장(refresh token, access token)
    response.set_cookie(
        key='access_token',
        value=str(refresh.access_token),
        httponly=True,
        secure=True,  # HTTPS를 사용할 경우 True로 설정
        samesite='Lax'
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=True,  # HTTPS를 사용할 경우 True로 설정
        samesite='Lax'
    )
    update_last_login(None, user)
    return response

# 로그아웃
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        # 쿠키 삭제
        response = HttpResponse("로그아웃 성공!!")
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        # refresh토큰 blacklist에 추가
        refresh_token = request.data.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return response
    
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
            # Update
            serializer.save()
            return Response({'serializer':serializer.data},
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
    
# 아이디(이메일) 찾기
@api_view(['POST'])
@permission_classes([AllowAny])
def find_userid(request):
    target_email = request.data.get('email')
    User = get_user_model()
    user = User.objects.filter(email=target_email)
    if not user.exists():
        return Response({'message': '해당 아이디는 존재하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    data = {'email' : user.first().email}
    return Response(data, status=status.HTTP_200_OK)

# 소셜 로그인(구글)
from django.shortcuts import redirect
import os
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from rest_framework import status
from .models import *
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view

def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


def google_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')

    # 1. 받은 코드로 구글에 access token 요청
    token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    
    ### 1-1. json으로 변환 & 에러 부분 파싱
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    ### 1-2. 에러 발생 시 종료
    if error is not None:
        raise JSONDecodeError(error)

    ### 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get('access_token')

    #################################################################

    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code

    user_info_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"
    response = requests.get(user_info_endpoint, headers={"Authorization": f"Bearer {access_token}"})
    ### 2-1. 에러 발생 시 400 에러 반환
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    ### 2-2. 성공 시 이메일 가져오기
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    user_info = response.json()
    name = user_info.get('name')

    # return JsonResponse({'access': access_token, 'email':email})

    #################################################################

    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        try:
            # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
            social_user = SocialAccount.objects.get(user=user)
            # 있는데 네이버 계정이 아니어도 에러
            if social_user.provider != 'google':
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        
        except SocialAccount.DoesNotExist:
            # 소셜 계정이 없으면 새로 생성
            social_user = SocialAccount(user=user, provider='google', uid=email, extra_data=user_info, last_login=now())
            social_user.save()

        # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 우저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/user/google/login/finish/", data=data)
        accept_status = accept.status_code
        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        user = User(email=email, name=name)  # 필요한 필드 채우기
        # 전화번호, 비밀번호, 사업자등록번호, 사업자등록증을 따로 입력받기
        user.set_unusable_password()
        user.save()
        # 새로운 소셜 계정 생성
        social_user = SocialAccount(user=user, provider='google', uid=email, last_login=now())
        social_user.save()

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/user/google/login/finish/", data=data)
        accept_status = accept.status_code
        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    
class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client

# 소셜 로그인(네이버)
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.naver import views as naver_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.utils.timezone import now

NAVER_CALLBACK_URI = BASE_URL + 'api/user/naver/callback/'

# 네이버 로그인 창
def naver_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    return redirect(f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&state=STATE_STRING&redirect_uri={NAVER_CALLBACK_URI}")

def naver_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_NAVER_SECRET")
    code = request.GET.get("code")
    state_string = request.GET.get("state")

    # code로 access token 요청
    token_request = requests.get(f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state_string}")
    token_response_json = token_request.json()

    error = token_response_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_response_json.get("access_token")

    # return JsonResponse({"access_token":access_token})

    # access token으로 네이버 프로필 요청
    profile_request = requests.post(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    response_data = profile_json.get("response")
    if response_data is None:
        return JsonResponse({'err_msg': 'failed to get user profile'}, status=status.HTTP_400_BAD_REQUEST)

    # 사용자 정보 추출
    email = response_data.get("email")
    name = response_data.get("name")
    phone = response_data.get("mobile")

    if email is None:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)

    # 받아온 네이버 계정으로 회원가입/로그인 시도
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        try:
            # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
            social_user = SocialAccount.objects.get(user=user)
            # 있는데 네이버 계정이 아니어도 에러
            if social_user.provider != 'naver':
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        
        except SocialAccount.DoesNotExist:
            # 소셜 계정이 없으면 새로 생성
            social_user = SocialAccount(user=user, provider='naver', uid=email, extra_data=response_data, last_login=now())
            social_user.save()

        # 이미 naver로 제대로 가입된 유저 => 로그인 & 해당 우저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/user/naver/login/finish/", data=data)
        accept_status = accept.status_code
        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        user = User(email=email, name=name, p_num=phone)  # 필요한 필드 채우기
        # 비밀번호, 사업자등록번호, 사업자등록증을 따로 입력받기
        user.set_unusable_password()
        user.save()

        # 새로운 소셜 계정 생성
        social_user = SocialAccount(user=user, provider='naver', uid=email, last_login=now())
        social_user.save()
        
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/user/naver/login/finish/", data=data)
        accept_status = accept.status_code
        # print(data, accept, accept_status)
        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

class NaverLogin(SocialLoginView):
    adapter_class = naver_view.NaverOAuth2Adapter
    callback_url = NAVER_CALLBACK_URI
    client_class = OAuth2Client