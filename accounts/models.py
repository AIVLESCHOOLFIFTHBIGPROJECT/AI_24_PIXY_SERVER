from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import os
from uuid import uuid4
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, name, p_num, r_num, password=None, bussiness_r=None):
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            p_num=p_num,
            r_num=r_num
        )

        if bussiness_r:
            user.bussiness_r = bussiness_r

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email,
            name=name,
            password=password,
        )

        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    def date_upload_to(instance, filename):
    # upload_to="%Y/%m/%d" 처럼 날짜로 세분화
        ymd_path = timezone.now().strftime('%Y/%m/%d') 
        # 길이 32 인 uuid 값
        uuid_name = uuid4().hex
        # 확장자 추출
        extension = os.path.splitext(filename)[-1].lower()
        # 결합 후 return
        return '/'.join([
            ymd_path,
            uuid_name + extension,
        ])
        
    email = models.EmailField(
        verbose_name='email',
        max_length=100,
        unique=True,
    )
    name = models.CharField(max_length=30)
    p_num = models.CharField(max_length=30)
    r_num = models.CharField(max_length=30)
    bussiness_r = models.ImageField("사업자등록증", upload_to=date_upload_to, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    # 동의여부(개인정보동의, 우리약관, 이메일수신 -> 선택사항)
    is_agreement1 = models.BooleanField(default=False)
    is_agreement2 = models.BooleanField(default=False)
    is_agreement3 = models.BooleanField(default=False, null=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'p_num', 'r_num']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
    class Meta:
        db_table = 'user' # 테이블명을 user로 설정