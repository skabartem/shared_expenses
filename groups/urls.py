from django.urls import path
from . import views

urlpatterns = [
    path('groups/', views.GroupsListView.as_view(), name="my-groups"),
    path('<str:pk>/', views.GroupDetailView.as_view(), name="detail"),

]