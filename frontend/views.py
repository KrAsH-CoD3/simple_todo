from urllib import request
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, LoginForm
from django.contrib.auth.models import AbstractUser, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

@login_required
@require_http_methods(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'frontend/task-list.html')

@require_http_methods(["GET", "POST"])
def register_user(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in
            messages.success(request, 'Registration successful!')
            return redirect('index')
        else:
            messages.error(request, 'Please Check your input')
    else: 
        form = UserRegistrationForm()
    return render(request, 'frontend/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_user(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user: User = form.get_user()
            login(request, user)
            return redirect('index')
        else:
            # form.add_error(None, 'Check bruv, check well => Invalid username or password')
            messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'frontend/login.html', {'form': form})


@require_http_methods(["GET"])
def logout_user(request: HttpRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect('login', )