from django.contrib import admin

from rewards.models import ActivityLog, Badge, EarnedBadge, Rank


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rarity', 'category')
    list_filter = ('rarity', 'category')
    search_fields = ('id', 'name')


@admin.register(EarnedBadge)
class EarnedBadgeAdmin(admin.ModelAdmin):
    list_display = ('child', 'badge', 'earned_at')
    search_fields = ('child__nickname', 'badge__name')


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'min_missions', 'order')
    ordering = ('order',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'type', 'title', 'xp_earned', 'created_at')
    list_filter = ('type',)
    search_fields = ('child__nickname', 'title')
