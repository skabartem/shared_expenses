from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from users.forms import SignUpForm, ProfileForm
from .models import Profile


class UserLogin(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('user-groups')


class SignUp(CreateView):
    form_class = SignUpForm
    template_name = 'users/register.html'

    def get_success_url(self):
        return reverse_lazy('login-user')


# Edit Profile View
class ProfileView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'users/details.html'


class UserLogout(LogoutView):
    template_name = 'users/details.html'
