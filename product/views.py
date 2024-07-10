from django.shortcuts import render
from rest_framework import generics
from .models import Product,Document
from .serializers import ProductSerializer,DocumentSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import AllowAny,IsAdminUser
from rest_framework.response import Response
from django.http import Http404
from rest_framework.parsers import MultiPartParser,FormParser
from drf_yasg.utils import swagger_auto_schema



#product
@swagger_auto_schema(
    method='get',
    responses={200: ProductSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    request_body=ProductSerializer,
    responses={201: ProductSerializer, 404: 'Not Found'}
)
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def ProductList(requset):
    #Read
    if requset.method=='GET':
         product=Product.objects.all()
         serializer=ProductSerializer(product,many=True)
         
         return Response(serializer.data)

    #Create
    elif requset.method=='POST':
        serializer=ProductSerializer(data=requset.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=404)



@swagger_auto_schema(
    method='get',
    responses={200: ProductSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=ProductSerializer,
    responses={200: ProductSerializer, 400: 'Bad Request'}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'}
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



#documnet
@swagger_auto_schema(
    method='get',
    responses={200: DocumentSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    request_body=DocumentSerializer,
    responses={201: DocumentSerializer, 404: 'Not Found'}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def document_list(request):
    if request.method == 'GET':
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: DocumentSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=DocumentSerializer,
    responses={200: DocumentSerializer, 400: 'Bad Request'}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def document_detail(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentSerializer(document)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)