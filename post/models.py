from django.db import models
from accounts.models import User
class Qna(models.Model):
    b_num = models.BigAutoField(primary_key=True)
    m_num = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=255)
    content=models.CharField(max_length=255,null=True)
    c_date = models.DateTimeField(auto_now_add=True)
    m_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Answer(models.Model):
    a_num = models.BigAutoField(primary_key=True)
    b_num = models.OneToOneField(Qna, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    c_date = models.DateTimeField(auto_now_add=True)
    m_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
