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
    # 비밀번호 찾기(이메일 인증을 통한 재설정 4가지)
    path('password_reset/', auth_views.PasswordResetView.as_view(email_template_name='registration/password_reset_email.txt'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # 구글 소셜 로그인
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),
    path('google/login/finish/', views.GoogleLogin.as_view(), name='google_login_todjango'),
    # 네이버 소셜 로그인
    path('naver/login/', views.naver_login, name='naver_login'),
    path('naver/callback/', views.naver_callback, name='naver_callback'),
    path('naver/login/finish/', views.NaverLogin.as_view(), name='naver_login_todjango'),
]