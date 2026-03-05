from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('characters.urls')),
    path('api/', include('missions.urls')),
    path('api/', include('rewards.urls')),
    path('api/', include('academy.urls')),
    path('api/', include('playground.urls')),
    path('api/', include('story.urls')),
]
