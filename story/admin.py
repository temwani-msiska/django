from django.contrib import admin

from story.models import Scene, SceneProgress, StoryArc


class SceneInline(admin.TabularInline):
    model = Scene
    extra = 0
    ordering = ['order']


@admin.register(StoryArc)
class StoryArcAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'arc_type', 'order', 'is_active')
    list_filter = ('arc_type', 'is_active')
    inlines = [SceneInline]


@admin.register(SceneProgress)
class SceneProgressAdmin(admin.ModelAdmin):
    list_display = ('child', 'scene', 'completed_at')
    list_filter = ('completed_at',)
