from django.urls import path
from . import views
urlpatterns = [
    path('',views.userprofile,name="account")
]
