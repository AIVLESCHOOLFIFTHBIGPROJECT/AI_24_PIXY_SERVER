from django.urls import path
from .views import ProductList,ProductDetail,SalesList,SalesDetail

urlpatterns = [
     path('product/',ProductList, name='product-list'),
     path('product/<int:pk>/',ProductDetail, name='product-detail'),
     path('sales/', SalesList, name='sales-list'),
     path('sales/<int:pk>/', SalesDetail, name='sales-detail'),
  
]
   