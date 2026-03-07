from django.urls import path

from story.views import SceneChoiceView, SceneCompleteView, StoryArcDetailView, StoryArcListView

urlpatterns = [
    path('story/arcs', StoryArcListView.as_view()),
    path('story/arcs/<slug:id>', StoryArcDetailView.as_view()),
    path('story/scenes/<uuid:id>/complete', SceneCompleteView.as_view()),
    path('story/scenes/<uuid:scene_id>/choice', SceneChoiceView.as_view()),
]
