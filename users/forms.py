from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

# Sign Up Form
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            ]


# Profile Form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'username',
            'email',
            'full_name',
            ]
