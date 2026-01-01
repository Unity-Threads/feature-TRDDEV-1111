from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from .models import UserProfile
from .forms import CustomPasswordChangeForm, EmailChangeForm
import re


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('profile')
    return render(request, 'profile/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile/profile.html', {'profile': profile})


@login_required
def ajax_save_profile(request):
    """AJAX update for name and email"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return JsonResponse({'success': False, 'error': 'Enter valid email'})

        request.user.username = name
        request.user.email = email
        request.user.save()
        return JsonResponse({'success': True, 'message': 'Profile updated successfully.'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def ajax_avatar_upload(request):
    """AJAX upload for avatar"""
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.avatar = request.FILES['avatar']
        profile.save()
        return JsonResponse({'success': True, 'avatar_url': profile.avatar.url})
    return JsonResponse({'success': False})


@login_required
def ajax_change_password(request):
    """AJAX password change — returns ONLY JSON (no alert popup)."""
    if request.method == 'POST':
        # Ensure we never use Django messages or redirects
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return JsonResponse({
                'success': True,
                'message': 'Password changed successfully!'
            })
        else:
            # Extract first error message cleanly
            first_error = list(form.errors.as_data().values())[0][0].messages[0]
            return JsonResponse({'success': False, 'error': first_error})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
