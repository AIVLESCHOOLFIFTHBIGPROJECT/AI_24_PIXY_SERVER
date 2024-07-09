from django.urls import path
from .views import ProductList,ProductDetail,document_list,document_detail

urlpatterns = [
     path('product/',ProductList, name='product-list'),
     path('product/<int:pk>/',ProductDetail, name='product-detail'),
     path('documents/',document_list, name='document_list'),
    path('documents/<int:pk>/',document_detail, name='document_detail'),
]
   