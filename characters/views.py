from rest_framework import generics

from characters.models import Character
from characters.serializers import CharacterSerializer


class CharacterListView(generics.ListAPIView):
    queryset = Character.objects.all().order_by('order')
    serializer_class = CharacterSerializer


class CharacterDetailView(generics.RetrieveAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    lookup_field = 'slug'
