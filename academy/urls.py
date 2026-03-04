from django.urls import path

from academy.views import CompleteLessonView, LearningTrackListView

urlpatterns = [
    path('academy/tracks', LearningTrackListView.as_view()),
    path('academy/lessons/<slug:id>/complete', CompleteLessonView.as_view()),
]
