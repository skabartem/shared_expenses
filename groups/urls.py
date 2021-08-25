from django.urls import path
from . import views

urlpatterns = [
    path('', views.GroupsListView.as_view(), name="user-groups"),
    path('<str:pk>/', views.GroupDetailView.as_view(), name="detail"),

    path('add-expense', views.ExpenseCreateView.as_view(), name="add-expense"),
]