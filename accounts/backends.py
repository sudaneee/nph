from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """Let students sign in with their email address (case-insensitive)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or password is None:
            return None
        User = get_user_model()
        for user in User.objects.filter(email__iexact=username.strip()):
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        User().set_password(password)  # equalise timing with the not-found path
        return None
