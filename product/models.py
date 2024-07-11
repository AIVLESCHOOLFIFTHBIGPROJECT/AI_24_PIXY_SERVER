from django.db import models
from store.models import Store

class Product(models.Model):
    p_num=models.BigAutoField(primary_key=True)
    s_num = models.ForeignKey(Store, on_delete=models.CASCADE,related_name='product',null=True,blank=True)
    name=models.CharField(max_length=255)
    price=models.IntegerField()
    sub_category=models.CharField(max_length=255,null=True)
    category=models.CharField(max_length=255,null=True)
    quantity=models.IntegerField(null=True)
    position=models.CharField(max_length=255,null=True)
    sales=models.IntegerField(null=True)
    date=models.CharField(max_length=255,null=True)
    
    def __str__(self):
        return self.name
    
    

class Sales(models.Model):
    s_num = models.BigAutoField(primary_key=True)
    p_num = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='sales_records')
    s_num2 = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_sales')
    s_rate = models.IntegerField()
    s_date = models.CharField(max_length=255)

    def __str__(self):
        return f"Sales {self.s_num}"


class Order(models.Model):
    s_num = models.BigAutoField(primary_key=True)
    p_num = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='order_records')
    s_num2 = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_orders')
    quantity = models.IntegerField()
    date = models.CharField(max_length=255)

    def __str__(self):
        return f"Order {self.s_num}"


# class Document(models.Model):
#     title = models.CharField(max_length=100)
#     uploaded_file = models.FileField(upload_to='product/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title