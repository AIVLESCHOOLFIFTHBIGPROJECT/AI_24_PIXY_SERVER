from django.db import models

class Product(models.Model):
    p_num=models.BigAutoField(primary_key=True)
    name=models.CharField(max_length=255)
    price=models.IntegerField()
    sub_category=models.CharField(max_length=255,null=True)
    category=models.CharField(max_length=255,null=True)
    quantity=models.IntegerField(null=True)
    position=models.CharField(max_length=255,null=True)
    sales=models.IntegerField(null=True)
    