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
    # path('profile_read/normal/', views.profile_read, name='profile_read'),
    # path('profile_update/normal/', views.profile_update, name='profile_update'),
]