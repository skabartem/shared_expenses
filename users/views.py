from django.shortcuts import render
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView
from users.forms import SignUpForm


class ProfileView(View):
    template_name = 'users/details.html'


class UserLogin(LoginView):
    template_name = 'users/login.html'


# class SignUp(generic.CreateView):
#     form_class = UserCreationForm
#     success_url = reverse_lazy('login')
#     template_name = 'users/register.html'

class SignUp(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'commons/signup.html'


class UserLogout(LogoutView):
    template_name = 'users/details.html'
