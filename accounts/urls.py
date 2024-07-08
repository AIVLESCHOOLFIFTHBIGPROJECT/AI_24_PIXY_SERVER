from django.urls import include, path
from . import views

# login_patterns = [
#     path('normal/', views.login, name='login'),
# ]

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/normal/', views.login, name='login'),
    path('logout/normal/', views.logout, name='logout'),
    path('logout_all/normal/', views.logout_all, name='logout_all'),
    path('profile/normal/', views.profile, name='profile'),
    path('delete_user/normal/', views.delete_user, name='delete_user'),
    path('find_userid/normal/', views.find_userid, name='find_userid'),
]