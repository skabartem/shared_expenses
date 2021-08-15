from django.urls import path
from . import views

urlpatterns = [
    path('', views.your_groups, name='groups'),
]