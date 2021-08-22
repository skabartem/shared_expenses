from django.urls import path
from .views import *


urlpatterns = [
    path('details/', ProfileView.as_view(), name='profile-details'),

]