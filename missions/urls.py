from django.urls import path

from missions.views import (
    BossBattlePhaseSubmitView,
    BossBattleStartView,
    MissionCompleteView,
    MissionDetailView,
    MissionListView,
    MissionSaveCodeView,
    MissionStartView,
    MissionStepSubmitView,
)

urlpatterns = [
    path('missions', MissionListView.as_view()),
    path('missions/<slug:id>', MissionDetailView.as_view()),
    path('missions/<slug:id>/start', MissionStartView.as_view()),
    path('missions/<slug:id>/complete', MissionCompleteView.as_view()),
    path('missions/<slug:id>/save-code', MissionSaveCodeView.as_view()),
    path('missions/<slug:id>/steps/<int:step_number>/submit', MissionStepSubmitView.as_view()),
    path('missions/<slug:id>/boss/start', BossBattleStartView.as_view()),
    path('missions/<slug:id>/boss/phase/<int:phase_number>/submit', BossBattlePhaseSubmitView.as_view()),
]
