from rest_framework import serializers
from .models import Product,Document

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('p_num','name','price','sub_category','quantity','position','sales')
        extra_kwargs = {
            'p_num': {'help_text':'상품시퀀스번호'},
            'name': {'help_text':'상품이름'},
            'price': {'help_text':'상품가격'},
            'sub_category': {'help_text':'상품서브카테고리'},
            'quantity': {'help_text':'상품카테고리'},
            'position': {'help_text':'상품위치'},
            'sales': {'help_text':'할인율'},

        }
        
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('title', 'uploaded_file', 'uploaded_at')
        extra_kwargs = {
            'title': {'help_text':'문서제목'},
            'uploaded_file': {'help_text':'문서업로드'},
            'uploaded_at': {'help_text':'업로드날짜'},
        }