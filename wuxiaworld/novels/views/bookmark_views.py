from wuxiaworld.novels.serializers import BookmarkSerializer, UpdateBookmarkSerializer
from wuxiaworld.novels.models import Bookmark, Profile, Novel, Chapter
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

class BookmarkSerializerView(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    queryset = Bookmark.objects.all()
    pagination_class = None
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.action in ["list", "create", "retreive", "delete"] and \
            self.request.user.is_authenticated:
            return self.queryset.filter(profile__user=self.request.user)
        return Bookmark.objects.none()
    def retrieve(self,request,pk):
        
        bookmark = get_object_or_404(Bookmark,novel__slug =  pk) 
        return Response(BookmarkSerializer(bookmark).data)
    def destroy(self,request, pk):
        bookmark = get_object_or_404(Bookmark,novel__slug =  pk) 
        profile = Profile.objects.get(user = request.user)
        profile.reading_lists.remove(bookmark)
        bookmark.delete()
        return Response({'message':'Bookmark removed'}, status=status.HTTP_200_OK)
    def create(self, request):
        novSlugChapSlug = request.data.get("novSlugChapSlug")
        novSlug = request.data.get("novSlug")
        if not novSlugChapSlug and not novSlug:
            return Response({'message':'novSlugChapSlug or novSlug not provided'},
             status = status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(user = request.user) 
        if novSlugChapSlug:
            chapter = get_object_or_404(Chapter, novSlugChapSlug = novSlugChapSlug)
            bookmark, created = Bookmark.objects.update_or_create(novel = chapter.novelParent, 
                        profile = profile, defaults={'chapter':chapter})

        elif novSlug:
            novel = get_object_or_404(Novel, slug = novSlug)
            bookmark, created = Bookmark.objects.update_or_create(novel = novel, 
                        profile = profile, defaults={'chapter':None})
        else: 
            return Response({'message':'novSlugChapSlug or novSlug not provided'},
             status = status.HTTP_404_NOT_FOUND)


        profile.reading_lists.add(bookmark)
        return Response(UpdateBookmarkSerializer(bookmark).data)

