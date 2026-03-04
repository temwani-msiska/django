from django.urls import path

from characters.views import CharacterDetailView, CharacterListView

urlpatterns = [
    path('characters', CharacterListView.as_view()),
    path('characters/<slug:slug>', CharacterDetailView.as_view()),
]
