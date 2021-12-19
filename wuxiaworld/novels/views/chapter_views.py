from wuxiaworld.novels.permissions import ReadOnly
from wuxiaworld.novels.models import Chapter, NovelViews, Settings, Bookmark
from wuxiaworld.novels.serializers import ChaptersSerializer, ChapterSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import Http404
from rest_framework_extensions.cache.decorators import (
    cache_response
)

class SingleChapterSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Chapter.objects.all()

    def retrieve(self, request, pk = None):
        obj = get_object_or_404(self.queryset,novSlugChapSlug = pk)
        novParent = obj.novelParent
        novelViewParent = NovelViews.objects.get(viewsNovelName = novParent.slug)
        novelViewParent.updateViews()
        serializer = ChapterSerializer(obj)
        if request.user.is_authenticated:
            try:
                userSettings = Settings.objects.get(profile__user=self.request.user)
                if userSettings.autoBookMark:
                    userBookmarks = Bookmark.objects.filter(profile__user=self.request.user,
                        novel = novParent)
                    if userBookmarks:
                        bookmark = userBookmarks.first()
                        if not bookmark.chapter or bookmark.chapter.index < obj.index:
                            bookmark.chapter = obj
                            bookmark.save()
                        
            except Exception as e:
                print(e)
        return Response(serializer.data)

    def list(self, request):
        raise Http404
 
class ChaptersSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Chapter.objects.all()
    serializer_class = ChaptersSerializer

    def retrieve(self, request, pk=None):
        queryset = Chapter.objects.filter(novelParent = pk).order_by(
            "index").only('index','title',"novSlugChapSlug","created_at")
        serializer = ChaptersSerializer(queryset, many = True)
        return Response(serializer.data)
         
    def list(self, request):
        queryset = Chapter.objects.filter(index = 1)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
