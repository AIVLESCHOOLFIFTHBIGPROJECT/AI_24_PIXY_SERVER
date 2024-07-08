from rest_framework import generics
from .models import Qna,Answer
from .serializers import QnaSerializer,AnswerSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAdminUser
from rest_framework.response import Response
from django.http import Http404


# @permission_classes([AllowAny])
# class QnaListCreate(generics.ListCreateAPIView):
#     queryset = Qna.objects.all()
#     serializer_class = QnaSerializer
    

# @permission_classes([AllowAny])
# class QnaRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Qna.objects.all()
#     serializer_class = QnaSerializer
    
    
# @permission_classes([AllowAny])
# class AnswerListCreate(generics.ListCreateAPIView):
#     queryset = Answer.objects.all()
#     serializer_class = AnswerSerializer
    
    
# @permission_classes([AllowAny])
# class AnswerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Answer.objects.all()
#     serializer_class = AnswerSerializer    
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def QnaList(requset):
    #Read
    if requset.method=='GET':
         qna=Qna.objects.all()
         serializer=QnaSerializer(qna,many=True)
         #many=True?->model.objects.all()로 검색한 객체는 list 형태 serializer는 한개의 객체만 이해가능 리스트는 이해못함 따라서 many=True추가해서 중복표현값에 대한 list를 받게끔한다
         return Response(serializer.data)

    #Create
    elif requset.method=='POST':
        serializer=QnaSerializer(data=requset.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=404)



@api_view(['GET','PUT','DELETE'])
@permission_classes([AllowAny])
def QnaDetail(requset,pk):
    try:
        qna=Qna.objects.get(pk=pk)
    except Qna.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    #Detail
    if requset.method=='GET':
        serializer=QnaSerializer(qna)
        return Response(serializer.data)
    
    #Update
    elif requset.method=='PUT':
        serializer=QnaSerializer(qna,data=requset.data)
        #requset요청이 들어온 qna를 serializer틀에 담아서 가져옴
        
        if serializer.is_valid():
             serializer.save()
             return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    #Delete
    elif requset.method=='DELETE':
        qna.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET','POST'])
@permission_classes([AllowAny])
def AnswerList(requset):
    #Read
    if requset.method=='GET':
         answer=Answer.objects.all()
         serializer=AnswerSerializer(answer,many=True)
         return Response(serializer.data)

    #Create
    elif requset.method=='POST':
        serializer=AnswerSerializer(data=requset.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=404)



@api_view(['GET','PUT','DELETE'])
@permission_classes([AllowAny])
def AnswerDetail(requset,pk):
    try:
        answer=Answer.objects.get(pk=pk)
    except Answer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    #Detail
    if requset.method=='GET':
        serializer=AnswerSerializer(answer)
        return Response(serializer.data)
    
    #Update
    elif requset.method=='PUT':
        serializer=AnswerSerializer(answer,data=requset.data)

        
        if serializer.is_valid():
             serializer.save()
             return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    #Delete
    elif requset.method=='DELETE':
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)