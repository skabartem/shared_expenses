from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from users.forms import SignUpForm, ProfileForm
from .models import Profile
from django.contrib.auth import login, logout

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.http import HttpResponseRedirect


class WelcomePage(TemplateView):
    template_name = 'users/welcome-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserLogin(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('user-groups')


@method_decorator(login_required, name='dispatch')
class UserLogout(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('/')


class SignUp(CreateView):
    form_class = SignUpForm
    template_name = 'users/register.html'

    def get_success_url(self):
        return reverse_lazy('login-user')

    def form_valid(self, form):
        valid = super().form_valid(form)

        # Login the user
        login(self.request, self.object)

        return valid


@method_decorator(login_required, name='dispatch')
class ProfileView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'users/details.html'

    def get_success_url(self):
        return reverse_lazy('user-groups')
