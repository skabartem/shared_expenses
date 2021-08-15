from django.urls import path
from . import views

urlpatterns = [
    path('details/', views.profile_details, name='profile-details'),
]