from django.db import models
from store.models import Store

class Product(models.Model):
    p_num=models.BigAutoField(primary_key=True)
    s_num = models.ForeignKey(Store, on_delete=models.CASCADE,related_name='product',null=True,blank=True)
    date=models.CharField(max_length=255,null=True)
    category=models.CharField(max_length=255,null=True)
    sales=models.IntegerField(null=True)
    holiday=models.BooleanField(null=True)
    promotion=models.IntegerField(null=True)
    stock=models.IntegerField(null=True)


    
    def __str__(self):
        return self.category
    
    

class Sales(models.Model):
    s_num = models.BigAutoField(primary_key=True)
    # p_num = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='sales_records')
    s_num2 = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_sales')
    date=models.CharField(max_length=255,null=True)
    category=models.CharField(max_length=255,null=True)
    sales=models.IntegerField(null=True)
    holiday=models.BooleanField(null=True)
    promotion=models.IntegerField(null=True)
    stock=models.IntegerField(null=True)

    def __str__(self):
        return self.s_num


