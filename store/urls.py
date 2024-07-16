from django.urls import path
from .views import StoreList,StoreDetail,StoreUploadList,StoreUploadDetail,PredictUploadList,PredictUploadDetail

urlpatterns = [
     path('store/',StoreList, name='store-list'),
     path('store/<int:pk>/',StoreDetail, name='store-detail'),
     path('stores/',StoreUploadList, name='store_upload-list'),
    path('stores/<int:pk>/',StoreUploadDetail, name='store_upload-detail'),
    path('predict/',PredictUploadList, name='predict_upload-list'),
    path('predict/<int:pk>/',PredictUploadDetail, name='predict_upload-list'),
]
   