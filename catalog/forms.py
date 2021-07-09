from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']
