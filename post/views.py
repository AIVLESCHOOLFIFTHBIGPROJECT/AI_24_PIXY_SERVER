# from rest_framework import generics
# from .models import Qna,Answer
# from .serializers import QnaSerializer,AnswerSerializer

# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny,IsAdminUser
# from rest_framework.response import Response
# from django.http import Http404
# from drf_yasg.utils import swagger_auto_schema


# # @permission_classes([AllowAny])
# # class QnaListCreate(generics.ListCreateAPIView):
# #     queryset = Qna.objects.all()
# #     serializer_class = QnaSerializer
    

# # @permission_classes([AllowAny])
# # class QnaRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
# #     queryset = Qna.objects.all()
# #     serializer_class = QnaSerializer
    
    
# # @permission_classes([AllowAny])
# # class AnswerListCreate(generics.ListCreateAPIView):
# #     queryset = Answer.objects.all()
# #     serializer_class = AnswerSerializer
    
    
# # @permission_classes([AllowAny])
# # class AnswerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
# #     queryset = Answer.objects.all()
# #     serializer_class = AnswerSerializer    
# @api_view(['GET','POST'])
# @permission_classes([AllowAny])
# def QnaList(requset):
#     #Read
#     if requset.method=='GET':
#          qna=Qna.objects.all()
#          serializer=QnaSerializer(qna,many=True)
#          #many=True?->model.objects.all()로 검색한 객체는 list 형태 serializer는 한개의 객체만 이해가능 리스트는 이해못함 따라서 many=True추가해서 중복표현값에 대한 list를 받게끔한다
#          return Response(serializer.data)

#     #Create
#     elif requset.method=='POST':
#         serializer=QnaSerializer(data=requset.data)
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=201)
#         return Response(serializer.errors,status=404)



# @api_view(['GET','PUT','DELETE'])
# @permission_classes([AllowAny])
# def QnaDetail(requset,pk):
#     try:
#         qna=Qna.objects.get(pk=pk)
#     except Qna.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
    
#     #Detail
#     if requset.method=='GET':
#         serializer=QnaSerializer(qna)
#         return Response(serializer.data)
    
#     #Update
#     elif requset.method=='PUT':
#         serializer=QnaSerializer(qna,data=requset.data)
#         #requset요청이 들어온 qna를 serializer틀에 담아서 가져옴
        
#         if serializer.is_valid():
#              serializer.save()
#              return Response(serializer.data)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
#     #Delete
#     elif requset.method=='DELETE':
#         qna.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



# @api_view(['GET','POST'])
# @permission_classes([AllowAny])
# def AnswerList(requset):
#     #Read
#     if requset.method=='GET':
#          answer=Answer.objects.all()
#          serializer=AnswerSerializer(answer,many=True)
#          return Response(serializer.data)

#     #Create
#     elif requset.method=='POST':
#         serializer=AnswerSerializer(data=requset.data)
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=201)
#         return Response(serializer.errors,status=404)



# @api_view(['GET','PUT','DELETE'])
# @permission_classes([AllowAny])
# def AnswerDetail(requset,pk):
#     try:
#         answer=Answer.objects.get(pk=pk)
#     except Answer.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
    
#     #Detail
#     if requset.method=='GET':
#         serializer=AnswerSerializer(answer)
#         return Response(serializer.data)
    
#     #Update
#     elif requset.method=='PUT':
#         serializer=AnswerSerializer(answer,data=requset.data)

        
#         if serializer.is_valid():
#              serializer.save()
#              return Response(serializer.data)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
#     #Delete
#     elif requset.method=='DELETE':
#         answer.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



from rest_framework import generics
from .models import Qna, Answer
from .serializers import QnaSerializer, AnswerSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    responses={200: QnaSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    request_body=QnaSerializer,
    responses={201: QnaSerializer, 404: 'Not Found'}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def QnaList(request):
    # Read
    if request.method == 'GET':
        qna = Qna.objects.all()
        serializer = QnaSerializer(qna, many=True)
        return Response(serializer.data)

    # Create
    elif request.method == 'POST':
        serializer = QnaSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=404)


@swagger_auto_schema(
    method='get',
    responses={200: QnaSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=QnaSerializer,
    responses={200: QnaSerializer, 400: 'Bad Request'}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def QnaDetail(request, pk):
    try:
        qna = Qna.objects.get(pk=pk)
    except Qna.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Detail
    if request.method == 'GET':
        serializer = QnaSerializer(qna)
        return Response(serializer.data)
    
    # Update
    elif request.method == 'PUT':
        serializer = QnaSerializer(qna, data=request.data)
        
        if serializer.is_valid():
             serializer.save()
             return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete
    elif request.method == 'DELETE':
        qna.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='get',
    responses={200: AnswerSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    request_body=AnswerSerializer,
    responses={201: AnswerSerializer, 404: 'Not Found'}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def AnswerList(request):
    # Read
    if request.method == 'GET':
        answer = Answer.objects.all()
        serializer = AnswerSerializer(answer, many=True)
        return Response(serializer.data)

    # Create
    elif request.method == 'POST':
        serializer = AnswerSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=404)


@swagger_auto_schema(
    method='get',
    responses={200: AnswerSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=AnswerSerializer,
    responses={200: AnswerSerializer, 400: 'Bad Request'}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def AnswerDetail(request, pk):
    try:
        answer = Answer.objects.get(pk=pk)
    except Answer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Detail
    if request.method == 'GET':
        serializer = AnswerSerializer(answer)
        return Response(serializer.data)
    
    # Update
    elif request.method == 'PUT':
        serializer = AnswerSerializer(answer, data=request.data)
        
        if serializer.is_valid():
             serializer.save()
             return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete
    elif request.method == 'DELETE':
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
