from django.shortcuts import render, get_object_or_404
from .models import Novel, Author, Category, Chapter
from .serializers import (NovelSerializer, CategorySerializer,
                        AuthorSerializer,ChaptersSerializer,ChapterSerializer,NovelInfoSerializer,
                        SearchSerializer)
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from .tasks import addCat, addNovel, addChaps
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from rest_framework import filters
from rest_framework import pagination

class SearchPagination(pagination.PageNumberPagination):       
    page_size = 5

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

class CategorySerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def retrieve(self, request, pk = None):
        try:
            pageReq = self.request.query_params.get('page')
            category = get_object_or_404(Category,id = pk)
            queryset = Novel.objects.filter(category = pk)
            if pageReq:
                items = int(pageReq)*10
                if items>10:
                    queryset = queryset[items-10:items]
                elif items==10:
                    queryset = queryset[:items]
                else:
                    raise Http404
                
            else:
                queryset = queryset[:10]
            if len(queryset)>0:
                serializer = NovelInfoSerializer(queryset, many = True)
                catSerial = CategorySerializer(category)
                finaldata = {'category':catSerial.data,'results':serializer.data}
                return Response(finaldata)
            else:
                raise Http404
        except Exception as e:
            print(e)
            raise Http404
    

class AuthorSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class SingleChapterSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Chapter.objects.all()
    serializer = ChapterSerializer(queryset)
    
    def retrieve(self, request, pk = None):
        object = get_object_or_404(self.queryset,novSlugChapSlug = pk)
        novParent = object.novelParent
        novParent.views = novParent.views+1
        
        novParent.save()
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
        obj.views = obj.views + 1
        obj.save(update_fields=("views",))
        return super().retrieve(request, *args, **kwargs)
    def list(self, request,*args, **kwargs):
        
        queryset = Novel.objects.all()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

class SearchSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.all()
    pagination_class = SearchPagination
    serializer_class = SearchSerializer
    search_fields = ['name','slug']
    filter_backends = (filters.SearchFilter,)

def catUpload(request):
    addCat.delay()
    return HttpResponse("<li>Done</li>")

def novelUpload(request):
    addNovel.delay()
    return HttpResponse("<li>Done</li>")

def chapUpload(request):
    
    addChaps.delay()
    return HttpResponse("<li>Done</li>")