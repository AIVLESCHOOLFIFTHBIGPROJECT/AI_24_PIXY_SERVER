from django.db import models

class Qna(models.Model):
    b_num = models.BigAutoField(primary_key=True)
    m_num = models.BigIntegerField()
    title = models.CharField(max_length=255)
    c_date = models.DateTimeField(auto_now_add=True)
    m_date = models.DateTimeField(auto_now=True)
    viewcnt = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Answer(models.Model):
    a_num = models.BigAutoField(primary_key=True)
    b_num = models.OneToOneField(Qna, on_delete=models.CASCADE)
    m_num = models.BigIntegerField()
    content = models.CharField(max_length=255)
    c_date = models.DateTimeField(auto_now_add=True)
    m_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
