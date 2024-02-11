from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from .models import *
from django import forms

class CustomRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-username', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input-email', 'placeholder': 'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-password', 'placeholder': 'Password...', 'autocomplete': 'new-password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-password-again', 'placeholder': 'Password again...', 'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class MyLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-username', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-password', 'placeholder': 'Password...', 'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ('username', 'password')