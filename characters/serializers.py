from rest_framework import serializers

from characters.models import Character, CharacterAbility, CharacterStat


class CharacterAbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterAbility
        fields = '__all__'


class CharacterStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterStat
        fields = '__all__'


class CharacterSerializer(serializers.ModelSerializer):
    abilities = CharacterAbilitySerializer(many=True, read_only=True)
    stats = CharacterStatSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = '__all__'
