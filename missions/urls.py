from django.urls import path

from missions.views import MissionCompleteView, MissionDetailView, MissionListView, MissionSaveCodeView, MissionStartView

urlpatterns = [
    path('missions', MissionListView.as_view()),
    path('missions/<slug:id>', MissionDetailView.as_view()),
    path('missions/<slug:id>/start', MissionStartView.as_view()),
    path('missions/<slug:id>/complete', MissionCompleteView.as_view()),
    path('missions/<slug:id>/save-code', MissionSaveCodeView.as_view()),
]
