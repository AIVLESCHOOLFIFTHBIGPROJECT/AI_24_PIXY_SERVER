# llm_model/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('start_learning/', views.start_learning, name='start_learning'),
    path('process_text/', views.process_text, name='process_text'),
]
