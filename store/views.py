from django.shortcuts import render
from .models import Store,StoreUpload,PredictUpload
from .serializers import StoreSerializer,StoreUploadSerializer,PredictUploadSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import Http404
from rest_framework.parsers import MultiPartParser,FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import csv
import os
from django.conf import settings
from product.models import Product,Sales
import pandas as pd
import pickle
import os
import boto3
from io import StringIO
# from django.contrib.auth.models import User


# Store
@swagger_auto_schema(
    method='get',
    tags=['Store'],
    operation_summary="List all stores",
    operation_description="Get a list of all store entries",
    responses={200: StoreSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    tags=['Store'],
    operation_summary="Create a new store",
    operation_description="Create a new store entry",
    request_body=StoreSerializer,
    responses={201: StoreSerializer, 400: 'Bad Request'}
)
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def StoreList(request):
    #Read
    if request.method=='GET':
         store=Store.objects.all()
         serializer=StoreSerializer(store,many=True)
         
         return Response(serializer.data)

    #Create
    elif request.method=='POST':
        serializer=StoreSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=404)

# store detail
@swagger_auto_schema(
    method='get',
    tags=['Store'],
    operation_summary="Retrieve a store",
    operation_description="Get details of a specific store entry",
    responses={200: StoreSerializer, 404: 'Not Found'}
)
@swagger_auto_schema(
    method='put',
    tags=['Store'],
    operation_summary="Update a store",
    operation_description="Update an existing store entry",
    request_body=StoreSerializer,
    responses={200: StoreSerializer, 400: 'Bad Request', 404: 'Not Found'}
)
@swagger_auto_schema(
    method='delete',
    tags=['Store'],
    operation_summary="Delete a store",
    operation_description="Delete a specific store entry",
    responses={204: 'No Content', 404: 'Not Found'}
)
@api_view(['GET','PUT','DELETE'])
@permission_classes([AllowAny])
def StoreDetail(request,pk):
    try:
        store=Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    #Detail
    if request.method=='GET':
        serializer=StoreSerializer(store)
        return Response(serializer.data)
    
    #Update
    elif request.method=='PUT':
        serializer=StoreSerializer(store,data=request.data)
        
        if serializer.is_valid():
             serializer.save()
             return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    #Delete
    elif request.method=='DELETE':
        store.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#StoreUpload
@swagger_auto_schema(
    method='get',
    tags=['StoreUpload'],
    operation_summary="List all store uploads",
    operation_description="Get a list of all store upload entries",
    responses={200: StoreUploadSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    tags=['StoreUpload'],
    operation_summary="Create a new store upload",
    operation_description="Create a new store upload entry and process CSV file",
    request_body=StoreUploadSerializer,
    responses={201: StoreUploadSerializer, 400: 'Bad Request'}
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
        try:
            # 현재 로그인된 사용자의 Store 정보 가져오기
            store = Store.objects.get(m_num=request.user)
        except Store.DoesNotExist:
            return Response({'error': 'Store not found for this user'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StoreUploadSerializer(data=request.data)
        if serializer.is_valid():
            store_upload = serializer.save(
                s_num=store,
                m_num=request.user
            )

            # S3에서 CSV 파일 가져오기
            file_url = store_upload.uploaded_file.url
            s3_client = boto3.client('s3')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3_key = file_url.split(f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]

            try:
                csv_obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
                body = csv_obj['Body']
                csv_string = body.read().decode('utf-8')
                reader = csv.DictReader(StringIO(csv_string))
                
                for row in reader:
                    Product.objects.create(
                        s_num=store_upload.s_num,
                        date=row['date'],
                        category=row['category'],
                        sales=row['sales'],
                        holiday=bool(int(row['holiday'])),  # 0과 1을 Boolean 으로 변환
                        promotion=row['promotion'],
                        stock=row['stock'],
                    )
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
# store upload detail
@swagger_auto_schema(
    method='get',
    tags=['StoreUpload'],
    operation_summary="Retrieve a store upload",
    operation_description="Get details of a specific store upload entry",
    responses={200: StoreUploadSerializer, 404: 'Not Found'}
)
@swagger_auto_schema(
    method='put',
    tags=['StoreUpload'],
    operation_summary="Update a store upload",
    operation_description="Update an existing store upload entry",
    request_body=StoreUploadSerializer,
    responses={200: StoreUploadSerializer, 400: 'Bad Request', 404: 'Not Found'}
)
@swagger_auto_schema(
    method='delete',
    tags=['StoreUpload'],
    operation_summary="Delete a store upload",
    operation_description="Delete a specific store upload entry",
    responses={204: 'No Content', 404: 'Not Found'}
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



#PredictUpload
@swagger_auto_schema(
    method='get',
    tags=['PredictUpload'],
    operation_summary="List all predict uploads",
    operation_description="Get a list of all store upload entries",
    responses={200: PredictUploadSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    tags=['PredictUpload'],
    operation_summary="Upload a CSV file and predict sales",
    operation_description="Upload a CSV file, predict sales using the trained model, and save the results to the Sales table",
    request_body=PredictUploadSerializer,
    responses={201: "Predictions saved to Sales table", 400: "Bad Request"}
)
@api_view(['GET','POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def PredictUploadList(request):
    if request.method=='GET':
        predict = PredictUpload.objects.all()
        serializer = PredictUploadSerializer(predict, many=True)
        return Response(serializer.data)
    elif request.method=='POST':
        try:
            # 현재 로그인된 사용자의 Store 정보 가져오기
            store = Store.objects.get(m_num=request.user)
        except Store.DoesNotExist:
            return Response({'error': 'Store not found for this user'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PredictUploadSerializer(data=request.data)
        if serializer.is_valid():
            predict_upload = serializer.save(
                s_num=store,
                m_num=request.user
            )

            # CSV 파일 S3에서 읽기
            file_url = predict_upload.uploaded_file.url
            s3_client = boto3.client('s3')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3_key = file_url.split(f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/')[1]

            try:
                csv_obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
                body = csv_obj['Body']
                csv_string = body.read().decode('utf-8')
                df = pd.read_csv(StringIO(csv_string))
                
                df.drop(columns='Unnamed: 0', axis=1, inplace=True)
                df2=pd.get_dummies(df, columns=['category'])
                df2=df2.set_index('date')

                # 모델 로드 (여기에서 파일명을 실제 파일명으로 변경)
                model_path = os.path.join(settings.BASE_DIR, 'media/weight', 'saved_model.pickle')
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)

                # 예측 
                df['predicted_sales'] = model.predict(df2)

                # 예측 결과 Sales 테이블에 저장
                for _, row in df.iterrows():
                    Sales.objects.create(
                        s_num2=predict_upload.s_num,
                        date=row['date'],
                        category=row['category'],
                        sales=row['predicted_sales'],
                        holiday=row['holiday'], # 0과 1을 Boolean으로 변환하지 않고 그대로 저장
                        promotion=row['promotion'],
                        stock=row['stock'],
                    )

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# PredictUploadDetail
@swagger_auto_schema(
    method='get',
    tags=['PredictUpload'],
    operation_summary="Retrieve a predict upload",
    operation_description="Get details of a specific predict upload entry",
    responses={200: PredictUploadSerializer, 404: 'Not Found'}
)
@swagger_auto_schema(
    method='put',
    tags=['PredictUpload'],
    operation_summary="Update a store upload",
    operation_description="Update an existing predict upload entry",
    request_body=PredictUploadSerializer,
    responses={200: PredictUploadSerializer, 400: 'Bad Request', 404: 'Not Found'}
)
@swagger_auto_schema(
    method='delete',
    tags=['PredictUpload'],
    operation_summary="Delete a predict upload",
    operation_description="Delete a specific predict upload entry",
    responses={204: 'No Content', 404: 'Not Found'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def PredictUploadDetail(request, pk):
    try:
        predict = PredictUpload.objects.get(pk=pk)
    except PredictUpload.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PredictUploadSerializer(predict)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = PredictUploadSerializer(predict, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        predict.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)