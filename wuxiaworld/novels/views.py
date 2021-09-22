from django.shortcuts import render, get_object_or_404
from .models import Novel, Author, Category, Chapter, NovelViews
from .serializers import (NovelSerializer, CategorySerializer,
                        AuthorSerializer,ChaptersSerializer,ChapterSerializer,NovelInfoSerializer,
                        SearchSerializer)
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.pagination import LimitOffsetPagination
from django.http import Http404
from rest_framework import filters
from rest_framework import pagination
from .tasks import initial_scrape, continous_scrape, add_novels
from .utils import delete_dupes, delete_unordered_chapters

class SearchPagination(pagination.LimitOffsetPagination):       
    page_size = 6

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            print(request)
            return True
        else:
            print(request.method in SAFE_METHODS)
            return request.method in SAFE_METHODS

class CategorySerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def retrieve(self, request, pk = None):
        
        pageReq = self.request.query_params.get('page')
        category = get_object_or_404(Category,slug = pk)
        queryset = Novel.objects.filter(category = category)
            
        if len(queryset)>0:
            page = self.paginate_queryset(queryset)
            serializer = NovelInfoSerializer(page, many=True)

            finaldata = {'category':category.name,'results':serializer.data,
                            }
            return Response(finaldata)
        else:
            raise Http404
        
    

class AuthorSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class SingleChapterSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Chapter.objects.all()

    def retrieve(self, request, pk = None):
        object = get_object_or_404(self.queryset,novSlugChapSlug = pk)
        novParent = object.novelParent
        novelViewParent = NovelViews.objects.get(viewsNovelName = novParent.slug)
        novelViewParent.updateViews()
        
        serializer = ChapterSerializer(object)
        return Response(serializer.data)
    def list(self, request):
        raise Http404
 

class ChaptersSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Chapter.objects.all()
    serializer_class = ChaptersSerializer

    def retrieve(self, request, pk=None):
        
        queryset = Chapter.objects.filter(novelParent = pk).order_by("index")
        if len(queryset)>0:
            serializer = ChaptersSerializer(queryset, many = True)
            return Response(serializer.data)
        else:
            raise Http404 
    def list(self, request):
        queryset = Chapter.objects.filter(index = 1)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

class NovelSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer
    
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        novelViews = NovelViews.objects.get(viewsNovelName = obj.slug)
        novelViews.updateViews()
        return super().retrieve(request, *args, **kwargs)
    # def list(self, request,*args, **kwargs):
        
    #     queryset = Novel.objects.all()
    #     page = self.paginate_queryset(queryset)
        
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return self.get_paginated_response(serializer.data)

class SearchSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.all()
    pagination_class = SearchPagination
    serializer_class = SearchSerializer
    search_fields = ['name','slug']
    filter_backends = (filters.SearchFilter,)

def addNovels(request):
    add_novels.delay()
    return HttpResponse("<li>Done</li>")

def deleteDuplicate(request):
    delete_dupes.delay()
    return HttpResponse("<li>Done</li>")

def deleteUnordered(request):
    delete_unordered_chapters.delay()
    return HttpResponse("<li>Done</li>")