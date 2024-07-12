
from django.urls import path
from .views import upload_video, lambda_callback

urlpatterns = [
    path('<int:store_id>/upload/', upload_video, name='upload_video'),
    path('callback/', lambda_callback, name='lambda_callback'),
]