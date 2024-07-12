from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/normal/', views.login, name='login'),
    path('logout/normal/', views.logout, name='logout'),
    path('logout_all/normal/', views.logout_all, name='logout_all'),
    path('profile/normal/', views.profile, name='profile'),
    path('delete_user/normal/', views.delete_user, name='delete_user'),
    path('find_userid/normal/', views.find_userid, name='find_userid'),
    # 토큰 재발급
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 구글 소셜 로그인
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),
    path('google/login/finish/', views.GoogleLogin.as_view(), name='google_login_todjango'),
    # 네이버 소셜 로그인
    path('naver/login/', views.naver_login, name='naver_login'),
    path('naver/callback/', views.naver_callback, name='naver_callback'),
    path('naver/login/finish/', views.NaverLogin.as_view(), name='naver_login_todjango'),
    # 이메일 인증(비밀번호 찾기)
    path('send-code/', views.send_verification_code, name='send_code'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
]