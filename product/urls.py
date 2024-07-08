from django.urls import path
from .views import ProductList,ProductDetail

urlpatterns = [
     path('product/', ProductList, name='product-list'),
    path('product/<int:pk>/',ProductDetail, name='product-detail'),
]
   