from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from .models import Profile

def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('core:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'account/register.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('core:home')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'You have been logged in!')
                return redirect('core:home')
            else:
                messages.error(request, 'Invalid email or password!')
    else:
        form = UserLoginForm()
    return render(request, 'account/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('account:login')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('account:profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'form': form,
        'balance': request.user.profile.balance
    }
    return render(request, 'account/profile.html', context)