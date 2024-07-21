from django.shortcuts import render
from rest_framework import generics
from .models import Product,Sales,Store
from .serializers import ProductSerializer,SalesSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import AllowAny,IsAdminUser
from rest_framework.response import Response
from django.http import Http404
from rest_framework.parsers import MultiPartParser,FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

#product
@swagger_auto_schema(
    method='get',
    tags=['Product'],
    operation_summary="List all products",
    operation_description="Get a list of all product entries",
    responses={200: ProductSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    tags=['Product'],
    operation_summary="Create a new product",
    operation_description="Create a new product entry",
    request_body=ProductSerializer,
    responses={201: ProductSerializer, 400: 'Bad Request'}
)
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def ProductList(requset):
   # Read
    if requset.method == 'GET':
        try:
            # 현재 로그인된 사용자의 Store 정보 가져오기
            store = Store.objects.get(m_num=requset.user)
        except Store.DoesNotExist:
            return Response({'error': 'Store not found for this user'}, status=status.HTTP_404_NOT_FOUND)
        
        # 로그인된 사용자의 s_num에 맞는 제품 필터링
        products = Product.objects.filter(s_num=store)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    #Create
    elif requset.method=='POST':
        serializer=ProductSerializer(data=requset.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=404)

### ProductDetail ###
@swagger_auto_schema(
    method='get',
    tags=['Product'],
    operation_summary="Retrieve a product",
    operation_description="Get details of a specific product entry",
    responses={200: ProductSerializer, 404: 'Not Found'}
)
@swagger_auto_schema(
    method='put',
    tags=['Product'],
    operation_summary="Update a product",
    operation_description="Update an existing product entry",
    request_body=ProductSerializer,
    responses={200: ProductSerializer, 400: 'Bad Request', 404: 'Not Found'}
)
@swagger_auto_schema(
    method='delete',
    tags=['Product'],
    operation_summary="Delete a product",
    operation_description="Delete a specific product entry",
    responses={204: 'No Content', 404: 'Not Found'}
)
@api_view(['GET','PUT','DELETE'])
@permission_classes([AllowAny])
def ProductDetail(requset,pk):
    try:
        product=Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    #Detail
    if requset.method=='GET':
        serializer=ProductSerializer(product)
        return Response(serializer.data)
    
    #Update
    elif requset.method=='PUT':
        serializer=ProductSerializer(product,data=requset.data)
        
        if serializer.is_valid():
             serializer.save()
             return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    #Delete
    elif requset.method=='DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# Sales
@swagger_auto_schema(
    method='get',
    tags=['Sales'],
    operation_summary="List all sales",
    operation_description="Get a list of all sales entries",
    responses={200: SalesSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    tags=['Sales'],
    operation_summary="Create a new sale",
    operation_description="Create a new sale entry",
    request_body=SalesSerializer,
    responses={201: SalesSerializer, 400: 'Bad Request'}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def SalesList(request):
    # Read
    if request.method == 'GET':
        try:
            # 현재 로그인된 사용자의 Store 정보 가져오기
            store = Store.objects.get(m_num=request.user)
        except Store.DoesNotExist:
            return Response({'error': 'Store not found for this user'}, status=status.HTTP_404_NOT_FOUND)
        
        # 로그인된 사용자의 s_num에 맞는 Sales 필터링
        sales = Sales.objects.filter(s_num2=store)
        serializer = SalesSerializer(sales, many=True)
        return Response(serializer.data)

    # Create
    elif request.method == 'POST':
        serializer = SalesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=404)

### Sales Detail ###
@swagger_auto_schema(
    method='get',
    tags=['Sales'],
    operation_summary="Retrieve a sale",
    operation_description="Get details of a specific sale entry",
    responses={200: SalesSerializer, 404: 'Not Found'}
)
@swagger_auto_schema(
    method='put',
    tags=['Sales'],
    operation_summary="Update a sale",
    operation_description="Update an existing sale entry",
    request_body=SalesSerializer,
    responses={200: SalesSerializer, 400: 'Bad Request', 404: 'Not Found'}
)
@swagger_auto_schema(
    method='delete',
    tags=['Sales'],
    operation_summary="Delete a sale",
    operation_description="Delete a specific sale entry",
    responses={204: 'No Content', 404: 'Not Found'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def SalesDetail(request, pk):
    try:
        sales = Sales.objects.get(pk=pk)
    except Sales.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Detail
    if request.method == 'GET':
        serializer = SalesSerializer(sales)
        return Response(serializer.data)

    # Update
    elif request.method == 'PUT':
        serializer = SalesSerializer(sales, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete
    elif request.method == 'DELETE':
        sales.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

