from django.urls import path
from .views import QnaListCreate, QnaRetrieveUpdateDestroy,AnswerListCreate,AnswerRetrieveUpdateDestroy

urlpatterns = [
    path('qna/', QnaListCreate.as_view(), name='qna-list'),
    path('qna/<int:pk>/', QnaRetrieveUpdateDestroy.as_view(), name='qna-detail'),
    path('answer/', AnswerListCreate.as_view(), name='answer-list'),
    path('answer/<int:pk>/', AnswerRetrieveUpdateDestroy.as_view(), name='answer-detail'),
]