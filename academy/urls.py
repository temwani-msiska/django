from django.urls import path

from academy.views import (
    CompleteLessonView,
    LearningTrackListView,
    LessonDetailView,
    LessonStartView,
    LessonStepSubmitView,
    SaveLessonDraftView,
)

urlpatterns = [
    path('academy/tracks', LearningTrackListView.as_view()),
    path('academy/lessons/<slug:slug>', LessonDetailView.as_view()),
    path('academy/lessons/<slug:slug>/start', LessonStartView.as_view()),
    path('academy/lessons/<slug:slug>/complete', CompleteLessonView.as_view()),
    path('academy/lessons/<slug:slug>/steps/<int:step_number>/submit', LessonStepSubmitView.as_view()),
    path('academy/lessons/<slug:slug>/steps/<int:step_number>/draft', SaveLessonDraftView.as_view()),
]
