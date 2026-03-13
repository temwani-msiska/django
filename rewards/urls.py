from django.urls import path

from rewards.views import BadgeListView

urlpatterns = [
    path('badges', BadgeListView.as_view()),
]
