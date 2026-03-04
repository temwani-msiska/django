from django.contrib import admin

from accounts.models import ChildPreferences, ChildProfile, ParentUser


@admin.register(ParentUser)
class ParentUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'name', 'username')


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'parent', 'avatar_character', 'level', 'xp', 'is_active')
    list_filter = ('avatar_character', 'is_active')
    search_fields = ('nickname', 'parent__email')


@admin.register(ChildPreferences)
class ChildPreferencesAdmin(admin.ModelAdmin):
    list_display = ('child', 'sound_enabled', 'music_enabled', 'high_contrast', 'public_profile', 'chat_locked')
    list_filter = ('sound_enabled', 'music_enabled', 'high_contrast', 'public_profile', 'chat_locked')
