from django.urls import path

from rewards.views import BadgeListView, RankListView

urlpatterns = [
    path('badges', BadgeListView.as_view()),
    path('ranks', RankListView.as_view()),
]
