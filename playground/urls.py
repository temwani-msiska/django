from django.urls import path

from playground.views import PlaygroundRunView

urlpatterns = [
    path('playground/run', PlaygroundRunView.as_view()),
]
