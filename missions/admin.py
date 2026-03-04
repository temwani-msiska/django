from django.contrib import admin

from missions.models import Mission, MissionProgress, MissionReward, MissionStep, StepProgress


class MissionStepInline(admin.TabularInline):
    model = MissionStep
    extra = 0


class MissionRewardInline(admin.TabularInline):
    model = MissionReward
    extra = 0


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'character', 'difficulty', 'xp', 'coins', 'is_active')
    list_filter = ('character', 'difficulty', 'is_active', 'language')
    search_fields = ('id', 'title', 'character__name')
    inlines = [MissionStepInline, MissionRewardInline]


@admin.register(MissionProgress)
class MissionProgressAdmin(admin.ModelAdmin):
    list_display = ('child', 'mission', 'status', 'progress', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('child__nickname', 'mission__title', 'mission__id')


@admin.register(MissionStep)
class MissionStepAdmin(admin.ModelAdmin):
    list_display = ('mission', 'num', 'title', 'validation_type')
    list_filter = ('validation_type',)
    search_fields = ('mission__id', 'title')


@admin.register(MissionReward)
class MissionRewardAdmin(admin.ModelAdmin):
    list_display = ('mission', 'type', 'label', 'value', 'badge')
    list_filter = ('type',)
    search_fields = ('mission__id', 'label')


@admin.register(StepProgress)
class StepProgressAdmin(admin.ModelAdmin):
    list_display = ('mission_progress', 'step', 'status', 'completed_at')
    list_filter = ('status',)
