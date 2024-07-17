from django.urls import path
from .views import ProductList,ProductDetail,SalesList,SalesDetail

urlpatterns = [
     path('product/',ProductList, name='product-list'),
     path('product/<int:pk>/',ProductDetail, name='product-detail'),
     path('sales/', SalesList, name='sales-list'),
     path('sales/<int:pk>/', SalesDetail, name='sales-detail'),
    #  path('order/', OrderList, name='order-list'),
    #  path('order/<int:pk>/', OrderDetail, name='order-detail'),
    #  path('documents/',document_list, name='document_list'),
    # path('documents/<int:pk>/',document_detail, name='document_detail'),
]
   