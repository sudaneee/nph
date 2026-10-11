from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile

User = get_user_model()

SIGNUP = {
    'first_name': 'Amina', 'last_name': 'Bello', 'email': 'Amina@Example.com',
    'phone': '0803 123 4567', 'password1': 'kano-2026-learn!', 'password2': 'kano-2026-learn!',
}


class SignUpLoginTests(TestCase):
    def test_signup_creates_user_profile_and_logs_in(self):
        resp = self.client.post(reverse('accounts:signup'), {**SIGNUP, 'next': '/courses/'})
        self.assertRedirects(resp, '/courses/', fetch_redirect_response=False)
        user = User.objects.get()
        self.assertEqual(user.email, 'amina@example.com')
        self.assertEqual(user.username, 'amina@example.com')
        self.assertEqual(Profile.objects.get(user=user).phone, '08031234567')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user('x', email='amina@example.com', password='x')
        resp = self.client.post(reverse('accounts:signup'), SIGNUP)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_signup_ignores_offsite_next(self):
        resp = self.client.post(reverse('accounts:signup'), {**SIGNUP, 'next': 'https://evil.example/'})
        self.assertRedirects(resp, reverse('accounts:dashboard'))

    def test_login_with_email(self):
        User.objects.create_user('someone', email='someone@example.com', password='pw-12345-abc')
        resp = self.client.post(reverse('accounts:login'), {'username': 'SOMEONE@example.com', 'password': 'pw-12345-abc'})
        self.assertRedirects(resp, reverse('accounts:dashboard'))

    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse('accounts:dashboard'))
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}")

    def test_dashboard_lists_enrolled_courses_with_progress(self):
        from learning.models import Enrollment
        from learning.tests import make_course
        course, _, _ = make_course()
        user = User.objects.create_user('d', email='d@example.com', password='pw')
        Enrollment.objects.create(user=user, course=course)
        self.client.force_login(user)
        resp = self.client.get(reverse('accounts:dashboard'))
        self.assertContains(resp, course.title)
        self.assertContains(resp, '0%')

    def test_profile_update_returns_to_next(self):
        user = User.objects.create_user('p', email='p@example.com', password='pw')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('accounts:profile')).status_code, 200)
        resp = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Musa', 'last_name': 'Sani', 'phone': '+2348031234567', 'next': '/courses/x/',
        })
        self.assertRedirects(resp, '/courses/x/', fetch_redirect_response=False)
        self.assertEqual(Profile.objects.get(user=user).phone, '+2348031234567')

    def test_password_reset_email_links_to_namespaced_confirm(self):
        User.objects.create_user('s', email='s@example.com', password='pw')
        self.client.post(reverse('accounts:password_reset'), {'email': 's@example.com'})
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/account/reset/', mail.outbox[0].body)
