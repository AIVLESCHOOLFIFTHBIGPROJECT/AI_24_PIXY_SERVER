from rest_framework import serializers
from .models import Qna,Answer

class QnaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qna
        fields = ('b_num','m_num','title','c_date','m_date','viewcnt')
        

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('a_num','b_num','m_num','content','c_date','m_date')