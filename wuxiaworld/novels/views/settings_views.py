from wuxiaworld.novels.permissions import ReadOnly
from wuxiaworld.novels.models import Settings
from wuxiaworld.novels.serializers import SettingsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status

class SettingsSerializerView(viewsets.ModelViewSet):
    serializer_class = SettingsSerializer
    queryset = Settings.objects.all()

    def get_queryset(self):
        if self.action in ['partial_update', 'update']:
            return self.queryset.filter(profile__user=self.request.user
                         )
        return Settings.objects.none()

    def create(self, request):
        return Response({'message':'Not allowed'},
             status = status.HTTP_404_NOT_FOUND)