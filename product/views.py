from django.shortcuts import render
from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAdminUser
from rest_framework.response import Response
from django.http import Http404





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
