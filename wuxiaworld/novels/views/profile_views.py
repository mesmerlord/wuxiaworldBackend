from wuxiaworld.novels.permissions import ReadOnly, IsOwner
from wuxiaworld.novels.models import Profile
from wuxiaworld.novels.serializers import ProfileSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

class ProfileSerializerView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsOwner, ReadOnly]
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(user=self.request.user)
        return Profile.objects.none()
