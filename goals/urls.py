from django.urls import path
from . import views



urlpatterns = [
    path('add_goal/', views.add_goal, name='add_goal'),
    path('list_goals/', views.list_goals, name='list_goals'),
    path('add_amount/<int:goal_id>/', views.add_amount, name='add_amount'),  
    path('delete_goal/<int:goal_id>/', views.delete_goal, name='delete_goal'),
]
