# api/urls.py
from django.urls import path
from .views import PredictCategory, UpdateDataset

urlpatterns = [
    path('predict-category/', PredictCategory.as_view(), name='predict-category'),
    path('update-dataset/', UpdateDataset.as_view(), name='update-dataset'),
]
