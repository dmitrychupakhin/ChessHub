from .forms import *
from django.shortcuts import render
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

class CustomRegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('main')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form(self.form_class)
        return context
    
    def get_success_url(self):
        return reverse_lazy('login')
    
class CustomLoginView(LoginView):
    form_class = MyLoginForm
    template_name = 'account/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form(self.form_class)
        return context
    
    def get_success_url(self):
        return reverse_lazy('game-home')

