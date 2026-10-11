from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from learning.models import Enrollment
from .forms import SignUpForm, ProfileForm
from .models import Profile


def _safe_next(request, default='accounts:dashboard'):
    nxt = request.POST.get('next') or request.GET.get('next')
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()},
                                               require_https=request.is_secure()):
        return nxt
    return default


def signup(request):
    if request.user.is_authenticated:
        return redirect(_safe_next(request))
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user, backend='accounts.backends.EmailBackend')
        messages.success(request, f'Welcome, {user.first_name}! Your account is ready.')
        return redirect(_safe_next(request))
    return render(request, 'accounts/signup.html', {
        'form': form, 'next': request.GET.get('next', ''), 'crumbs': [('Create account', None)],
    })


@login_required
def dashboard(request):
    enrollments = (Enrollment.objects.filter(user=request.user)
                   .select_related('course', 'certificate').order_by('-enrolled_at'))
    rows = [(e, e.progress_percent()) for e in enrollments]
    return render(request, 'accounts/dashboard.html', {
        'rows': rows, 'crumbs': [('My Learning', None)],
    })


@login_required
def profile(request):
    profile_obj = Profile.for_user(request.user)
    form = ProfileForm(request.POST or None, instance=request.user, profile=profile_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect(_safe_next(request, 'accounts:profile'))
    return render(request, 'accounts/profile.html', {
        'form': form, 'next': request.GET.get('next', ''),
        'crumbs': [('My Learning', '/account/'), ('Profile', None)],
    })
