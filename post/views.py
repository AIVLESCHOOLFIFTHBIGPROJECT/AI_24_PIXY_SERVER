from rest_framework import generics
from .models import Qna,Answer
from .serializers import QnaSerializer,AnswerSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAdminUser


@permission_classes([AllowAny])
class QnaListCreate(generics.ListCreateAPIView):
    queryset = Qna.objects.all()
    serializer_class = QnaSerializer
    

@permission_classes([AllowAny])
class QnaRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Qna.objects.all()
    serializer_class = QnaSerializer
    
    
@permission_classes([AllowAny])
class AnswerListCreate(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    
    
@permission_classes([AllowAny])
class AnswerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer    

