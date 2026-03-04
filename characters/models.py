import uuid

from django.db import models


class Character(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=20)
    title = models.CharField(max_length=50)
    description = models.TextField()
    backstory = models.TextField()
    quote = models.CharField(max_length=200)
    primary_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7)
    bg_color = models.CharField(max_length=7)
    order = models.IntegerField(default=0)


class CharacterAbility(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='abilities')
    emoji = models.CharField(max_length=10)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)


class CharacterStat(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='stats')
    label = models.CharField(max_length=30)
    value = models.IntegerField()
