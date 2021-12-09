from wuxiaworld.novels.models import Review
from wuxiaworld.novels.serializers import ReviewSerializer
from rest_framework import viewsets, status
from rest_framework import permissions

class ReviewSerializerView(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, permissions.DjangoModelPermissionsOrAnonReadOnly,)
