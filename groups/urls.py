from django.urls import path
from . import views

urlpatterns = [
    path('settle-up/', views.SettleUpView.as_view(), name="settle-up"),
    path('add-expense/', views.ExpenseCreateView.as_view(), name="add-expense"),
    path('expense/<str:pk>/', views.ExpenseUpdateView.as_view(), name="expense"),
    path('expense/<str:pk>/delete', views.ExpenseDeleteView.as_view(), name="delete-expense"),

    path('create-group/', views.GroupCreateView.as_view(), name="create-group"),
    path('<str:pk>/', views.GroupDetailView.as_view(), name="detail"),
]

