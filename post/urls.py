from django.urls import path
from .views import QnaList,QnaDetail,AnswerList,AnswerDetail

urlpatterns = [
    path('qna/', QnaList, name='qna-list'),
    path('qna/<int:pk>/',QnaDetail, name='qna-detail'),
    path('answer/',AnswerList, name='answer-list'),
    path('answer/<int:pk>/',AnswerDetail, name='answer-detail'),
]