from rest_framework import serializers
from .models import Qna,Answer

class QnaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qna
        fields = ('b_num','m_num','title','c_date','m_date','viewcnt')
        extra_kwargs = {
            'b_num': {'help_text':'게시판시퀀스번호'},
            'm_num': {'help_text':'회원시퀀스번호'},
            'title': {'help_text':'제목'},
            'c_date': {'help_text':'등록일'},
            'm_date': {'help_text':'수정일'},
            'viewcnt': {'help_text':'조회수'},

        }
        

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('a_num','b_num','m_num','content','c_date','m_date')
        extra_kwargs = {
            'a_num': {'help_text':'답글시퀀스번호'},
            'b_num': {'help_text':'게시판시퀀스번호'},
            'm_num': {'help_text':'회원시퀀스번호'},
            'content': {'help_text':'답글내용'},
            'c_date': {'help_text':'등록일'},
            'm_date': {'help_text':'수정일'},

        }