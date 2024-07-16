from django.urls import path
from .views import StoreList,StoreDetail,StoreUploadList,StoreUploadDetail

urlpatterns = [
     path('store/',StoreList, name='store-list'),
     path('store/<int:pk>/',StoreDetail, name='store-detail'),
     path('stores/',StoreUploadList, name='store_upload-list'),
    path('stores/<int:pk>/',StoreUploadDetail, name='store_upload-detail'),
]
   