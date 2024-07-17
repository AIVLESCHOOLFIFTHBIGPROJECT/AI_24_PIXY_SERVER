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

# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = '__all__'
#         extra_kwargs = {
#             's_num': {'help_text':'재고시퀀스번호'},
#             'p_num': {'help_text':'상품시퀀스번호'},
#             's_num2': {'help_text':'매장시퀀스번호'},
#             'quantity': {'help_text':'수량'},
#             'date': {'help_text':'발주날짜'},
#         }
        
# class DocumentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Document
#         fields = ('title', 'uploaded_file', 'uploaded_at')
#         extra_kwargs = {
#             'title': {'help_text':'문서제목'},
#             'uploaded_file': {'help_text':'문서업로드'},
#             'uploaded_at': {'help_text':'업로드날짜'},
#         }