from django.contrib import admin
from .models import Store,StoreUpload,PredictUpload

admin.site.register(Store)
admin.site.register(StoreUpload)
admin.site.register(PredictUpload)