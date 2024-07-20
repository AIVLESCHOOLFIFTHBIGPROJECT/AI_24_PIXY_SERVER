from rest_framework import serializers
from .models import Product,Sales

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'p_num': {'help_text':'상품시퀀스번호'},
            's_num': {'help_text':'판매시퀀스번호'},
            'date': {'help_text':'상품날짜'},
            'category':{'help_text':'상품카테고리'},
            'sales': {'help_text':'판매량'},
            'holiday': {'help_text':'휴일여부'},
            'promotion': {'help_text':'할인여부'},
            'stock': {'help_text':'재고'},
            
        }



class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sales
        fields = '__all__'
        extra_kwargs = {
            's_num': {'help_text':'판매시퀀스번호'},
            # 'p_num': {'help_text':'상품시퀀스번호'},
            's_num2': {'help_text':'매장시퀀스번호'},
            'date': {'help_text':'상품날짜'},
            'category':{'help_text':'상품카테고리'},
            'sales': {'help_text':'판매량'},
            'holiday': {'help_text':'휴일여부'},
            'promotion': {'help_text':'할인여부'},
            'stock': {'help_text':'재고'},
        }

