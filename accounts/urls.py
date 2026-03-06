from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    ChildActivityView,
    ChildCreateView,
    ChildLoginView,
    ChildMeView,
    ChildPreferencesView,
    ChildProgressView,
    ChildScreenTimeView,
    ConfirmEmailView,
    ParentLoginView,
    ParentMeView,
    ParentRegisterView,
    ResendConfirmationView,
    logout_view,
)

urlpatterns = [
    path('auth/parent/register', ParentRegisterView.as_view()),
    path('auth/parent/login', ParentLoginView.as_view()),
    path('auth/child/create', ChildCreateView.as_view()),
    path('auth/child/login', ChildLoginView.as_view()),
    path('auth/token/refresh', TokenRefreshView.as_view()),
    path('auth/logout', logout_view),
    path('auth/confirm-email', ConfirmEmailView.as_view()),
    path('auth/resend-confirmation', ResendConfirmationView.as_view()),
    path('user/me', ChildMeView.as_view()),
    path('user/progress', ChildProgressView.as_view()),
    path('user/preferences', ChildPreferencesView.as_view()),
    path('parent/me', ParentMeView.as_view()),
    path('parent/children/<uuid:id>/screen-time', ChildScreenTimeView.as_view()),
    path('parent/children/<uuid:id>/activity', ChildActivityView.as_view()),
]
