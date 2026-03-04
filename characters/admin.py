from django.contrib import admin

from characters.models import Character, CharacterAbility, CharacterStat


class CharacterAbilityInline(admin.TabularInline):
    model = CharacterAbility
    extra = 0


class CharacterStatInline(admin.TabularInline):
    model = CharacterStat
    extra = 0


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'title', 'order')
    search_fields = ('slug', 'name', 'title')
    inlines = [CharacterAbilityInline, CharacterStatInline]


@admin.register(CharacterAbility)
class CharacterAbilityAdmin(admin.ModelAdmin):
    list_display = ('character', 'emoji', 'title')
    search_fields = ('character__name', 'title')


@admin.register(CharacterStat)
class CharacterStatAdmin(admin.ModelAdmin):
    list_display = ('character', 'label', 'value')
    search_fields = ('character__name', 'label')
