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


class Document(models.Model):
    title = models.CharField(max_length=100)
    uploaded_file = models.FileField(upload_to='product/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title