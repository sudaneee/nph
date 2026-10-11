import re

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

PHONE_RE = re.compile(r'^\+?\d{10,15}$')


def clean_phone_number(value):
    phone = re.sub(r'[\s()-]', '', value or '')
    if phone and not PHONE_RE.match(phone):
        raise forms.ValidationError('Enter a valid phone number, e.g. 08012345678.')
    return phone


class SignUpForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'placeholder': '08012345678', 'autocomplete': 'tel'}))
    password1 = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Confirm password', strip=False, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'autocomplete': 'email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('first_name', 'last_name', 'email'):
            self.fields[name].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists. Try logging in.')
        return email

    def clean_phone(self):
        return clean_phone_number(self.cleaned_data['phone'])

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'The two passwords do not match.')
        elif p1:
            user = User(email=cleaned.get('email', ''), first_name=cleaned.get('first_name', ''),
                        last_name=cleaned.get('last_name', ''))
            try:
                password_validation.validate_password(p1, user)
            except forms.ValidationError as exc:
                self.add_error('password1', exc)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            from .models import Profile
            Profile.objects.update_or_create(user=user, defaults={'phone': self.cleaned_data['phone']})
        return user


class EmailLoginForm(AuthenticationForm):
    username = forms.CharField(label='Email', widget=forms.EmailInput(
        attrs={'autofocus': True, 'autocomplete': 'email', 'placeholder': 'you@example.com'}))


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'autocomplete': 'tel'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        if profile:
            self.fields['phone'].initial = profile.phone

    def clean_phone(self):
        return clean_phone_number(self.cleaned_data['phone'])

    def save(self, commit=True):
        user = super().save(commit=commit)
        self.profile.phone = self.cleaned_data['phone']
        self.profile.save()
        return user
