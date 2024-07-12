from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.notice_create),
    path('', views.notice_list, name='notice_list'),
    path('<int:pk>', views.notice_detail, name='notice_detail'),
    path('update/<int:pk>', views.notice_update, name='notice_update'),
    path('delete/<int:pk>', views.notice_delete, name='notice_delete')
]