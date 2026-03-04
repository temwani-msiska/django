from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class ParentUserEmailBackend(ModelBackend):
    """Authenticate using email (case-insensitive) and allow username fallback."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if password is None:
            return None

        UserModel = get_user_model()
        login_value = kwargs.get(UserModel.USERNAME_FIELD) or username
        if not login_value:
            return None

        user = None
        if hasattr(UserModel, 'email'):
            user = UserModel._default_manager.filter(email__iexact=login_value).first()

        if user is None and hasattr(UserModel, 'username'):
            user = UserModel._default_manager.filter(username=login_value).first()

        if user is not None and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
