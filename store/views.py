from django.shortcuts import render
from rest_framework import generics
from .models import Store,StoreUpload
from .serializers import StoreSerializer,StoreUploadSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import AllowAny,IsAdminUser
from rest_framework.response import Response
from django.http import Http404
from rest_framework.parsers import MultiPartParser,FormParser
from drf_yasg.utils import swagger_auto_schema



#store
@swagger_auto_schema(
    method='get',
    responses={200: StoreSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    request_body=StoreSerializer,
    responses={201: StoreSerializer, 404: 'Not Found'}
)
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def StoreList(requset):
    #Read
    if requset.method=='GET':
         store=Store.objects.all()
         serializer=StoreSerializer(store,many=True)
         
         return Response(serializer.data)

    #Create
    elif requset.method=='POST':
        serializer=StoreSerializer(data=requset.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=404)



@swagger_auto_schema(
    method='get',
    responses={200: StoreSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=StoreSerializer,
    responses={200: StoreSerializer, 400: 'Bad Request'}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'}
)
@api_view(['GET','PUT','DELETE'])
@permission_classes([AllowAny])
def StoreDetail(requset,pk):
    try:
        store=Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    #Detail
    if requset.method=='GET':
        serializer=StoreSerializer(store)
        return Response(serializer.data)
    
    #Update
    elif requset.method=='PUT':
        serializer=StoreSerializer(store,data=requset.data)
        
        if serializer.is_valid():
             serializer.save()
             return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    #Delete
    elif requset.method=='DELETE':
        store.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#StoreUpload
@swagger_auto_schema(
    method='get',
    responses={200: StoreUploadSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    request_body=StoreUploadSerializer,
    responses={201: StoreUploadSerializer, 404: 'Not Found'}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def StoreUploadList(request):
    if request.method == 'GET':
        stores = StoreUpload.objects.all()
        serializer = StoreUploadSerializer(stores, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = StoreUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: StoreUploadSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=StoreUploadSerializer,
    responses={200: StoreUploadSerializer, 400: 'Bad Request'}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def StoreUploadDetail(request, pk):
    try:
        stores = StoreUpload.objects.get(pk=pk)
    except StoreUpload.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StoreUploadSerializer(stores)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = StoreUploadSerializer(stores, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        stores.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)