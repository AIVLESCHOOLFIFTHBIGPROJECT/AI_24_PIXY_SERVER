from rest_framework import serializers
from .models import Store,StoreUpload

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
        extra_kwargs = {
            's_num': {'help_text':'매장시퀀스번호'},
            'm_num': {'help_text':'회원시퀀스번호'},
            'name': {'help_text':'매장이름'},
        }
        
class StoreUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreUpload
        fields = '__all__'
        extra_kwargs = {
            'u_num': {'help_text':'업로드시퀀스번호'},
            's_num': {'help_text':'매장시퀀스번호'},
            'm_num': {'help_text':'회원시퀀스번호'},
            'f_name': {'help_text':'파일명'},
        }