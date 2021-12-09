from wuxiaworld.novels.models import Announcement
from wuxiaworld.novels.serializers import AnnouncementSerializer
from rest_framework import viewsets, status
from rest_framework import permissions

class AnnouncementSerializerView(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly,)

    def get_queryset(self):
        return super().get_queryset().filter(published = True)
    