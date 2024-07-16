from django.db import models
from django.conf import settings

# Create your models here.
class Notice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='author')  # 작성자는 유저 !
    title = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) # 생성시 자동으로 시간저장
    updated_at = models.DateTimeField(auto_now=True) # 수정시 자동으로 시간저장

# 테이블명을 따로 지정
    class Meta:
        db_table = 'notice'
        ordering = ['-id'] # 정렬기준 최신순(늦게 작성된 글이 최신글임)