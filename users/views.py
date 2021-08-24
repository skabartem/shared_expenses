from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from users.forms import SignUpForm, ProfileForm
from django.contrib.auth.models import User
from .models import Profile


class UserLogin(LoginView):
    template_name = 'users/login.html'


class SignUp(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login-user')
    template_name = 'users/register.html'


# Edit Profile View
class ProfileView(UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy('login')
    template_name = 'users/details.html'


class UserLogout(LogoutView):
    template_name = 'users/details.html'
