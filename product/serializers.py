from rest_framework import serializers
from .models import Product,Document

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('p_num','name','price','sub_category','quantity','position','sales')
        
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'title', 'uploaded_file', 'uploaded_at')