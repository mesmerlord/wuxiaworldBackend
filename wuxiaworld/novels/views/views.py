from django.shortcuts import render, get_object_or_404
from ..models import Novel, Author, Category, Chapter, NovelViews, Profile, Tag, Bookmark, Settings
from ..serializers import (NovelSerializer, CategorySerializer,
                        AuthorSerializer,ChaptersSerializer,ChapterSerializer,NovelInfoSerializer,
                        SearchSerializer, ProfileSerializer,TagSerializer, BookmarkSerializer,
                        SettingsSerializer)
from rest_framework import viewsets, status, filters, pagination
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import Http404
from ..tasks import  add_novels, add_sources
from ..utils import delete_dupes, delete_unordered_chapters
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from ..permissions import *
from rest_framework.decorators import action

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

class SearchPagination(pagination.LimitOffsetPagination):       
    page_size = 6

class CategorySerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def retrieve(self, request, pk = None):
        category = get_object_or_404(Category,slug = pk)
        queryset = Novel.objects.filter(category = category)
        page = self.paginate_queryset(queryset)
        serializer = NovelSerializer(page, many=True)
        finaldata = {'category':category.name,'results':serializer.data,'count':queryset.count()}
        return Response(finaldata)
        
class TagSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    def retrieve(self, request, pk = None):
        tag = get_object_or_404(Tag,slug = pk)
        queryset = Novel.objects.filter(tag = tag)
        page = self.paginate_queryset(queryset)
        serializer = NovelInfoSerializer(page, many=True)
        finaldata = {'tag':tag.name,'results':serializer.data}
        return Response(finaldata)
        
class AuthorSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

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
        queryset = Chapter.objects.filter(novelParent = pk).order_by("index")
        serializer = ChaptersSerializer(queryset, many = True)
        return Response(serializer.data)
         
    def list(self, request):
        queryset = Chapter.objects.filter(index = 1)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class NovelSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        novelViews = NovelViews.objects.get(viewsNovelName = obj.slug)
        novelViews.updateViews()
        
        return super().retrieve(request, *args, **kwargs)

class SearchSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.all()
    pagination_class = SearchPagination
    serializer_class = SearchSerializer
    search_fields = ['name','slug']
    filter_backends = (filters.SearchFilter,)

class ProfileSerializerView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsOwner, ReadOnly]
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(user=self.request.user)
        return Profile.objects.none()

class BookmarkSerializerView(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    queryset = Bookmark.objects.all()
    pagination_class = None

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
        if novSlugChapSlug:
            chapter = get_object_or_404(Chapter, novSlugChapSlug = novSlugChapSlug)
            bookmark, created = Bookmark.objects.update_or_create(novel = chapter.novelParent, 
                        profile__user = request.user, defaults={'chapter':chapter})
        elif novSlug:
            novel = get_object_or_404(Novel, slug = novSlug)
            bookmark, created = Bookmark.objects.update_or_create(novel = novel, 
                        profile__user = request.user)
        profile = Profile.objects.get(user = request.user)
        profile.reading_lists.add(bookmark)
        return Response(BookmarkSerializer(bookmark).data)

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

def addNovels(request):
    add_novels.delay()
    return HttpResponse("<li>Done</li>")

def addSources(request):
    add_sources.delay()
    return HttpResponse("<li>Done</li>")

def deleteDuplicate(request):
    delete_dupes.delay()
    return HttpResponse("<li>Done</li>")

def deleteUnordered(request):
    delete_unordered_chapters.delay()
    return HttpResponse("<li>Done</li>")

def siteMap(request, *args,**kwargs):
    allNovels = Novel.objects.values_list('slug', 'created_at').all()
    siteName = kwargs['site'].split("-")
    top = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    bottom = "</urlset>"
    sitemap = top+"\n".join([f"<url><loc>https://www.{siteName[0]}.{siteName[1]}/novel/{x[0]}</loc><lastmod>{x[1].date()}</lastmod></url>" \
                for x in allNovels]) + bottom
    return HttpResponse(sitemap, content_type='text/xml')
