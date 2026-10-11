from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import EmailLoginForm

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('certificates/', views.certificates, name='certificates'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html', authentication_form=EmailLoginForm,
        redirect_authenticated_user=True, extra_context={'crumbs': [('Log in', None)]},
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/emails/password_reset_email.txt',
        subject_template_name='accounts/emails/password_reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done'),
        extra_context={'crumbs': [('Reset password', None)]},
    ), name='password_reset'),
    path('password-reset/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
        extra_context={'crumbs': [('Reset password', None)]},
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete'),
        extra_context={'crumbs': [('Reset password', None)]},
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
        extra_context={'crumbs': [('Reset password', None)]},
    ), name='password_reset_complete'),
]
