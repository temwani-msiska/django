from django.contrib import admin

from academy.models import LearningTrack, Lesson, LessonProgress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


@admin.register(LearningTrack)
class LearningTrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'order')
    search_fields = ('id', 'title')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'track', 'duration', 'order')
    list_filter = ('track',)
    search_fields = ('id', 'title', 'track__title')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('child', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed',)
    search_fields = ('child__nickname', 'lesson__title', 'lesson__id')
