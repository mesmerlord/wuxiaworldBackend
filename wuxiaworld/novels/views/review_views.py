from wuxiaworld.novels.models import Review
from wuxiaworld.novels.serializers import ReviewSerializer
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response

class ReviewSerializerView(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner_user.user == request.user:
            return super().update(self, request, *args, **kwargs)
        else:
            return Response("Not Authorized", 404)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner_user.user == request.user:
            return super().partial_update(self, request, *args, **kwargs)
        else:
            return Response("Not Authorized", 404)
    
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner_user.user == request.user:
            return super().destroy(self, request, *args, **kwargs)
        else:
            return Response("Not Authorized", 404)