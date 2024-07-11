from django.db import models
from accounts.models import User
class Store(models.Model):
    s_num = models.BigAutoField(primary_key=True)
    m_num = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class StoreUpload(models.Model):
    u_num = models.BigAutoField(primary_key=True)
    s_num = models.ForeignKey(Store, on_delete=models.CASCADE)
    m_num = models.ForeignKey(User, on_delete=models.CASCADE)
    f_name = models.CharField(max_length=255)

    def __str__(self):
        return self.f_name
