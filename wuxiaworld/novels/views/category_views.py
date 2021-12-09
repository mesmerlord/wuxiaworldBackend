from wuxiaworld.novels.serializers import (CategorySerializer, NovelSerializer,
                                TagSerializer, AuthorSerializer,NovelInfoSerializer )
from wuxiaworld.novels.models import Novel, Category, Tag, Author
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
from wuxiaworld.novels.permissions import ReadOnly
from rest_framework.pagination import LimitOffsetPagination
from wuxiaworld.novels.views.cache_utils import DefaultKeyConstructor
from rest_framework_extensions.cache.decorators import (
    cache_response
)

class CategorySerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_classes = LimitOffsetPagination

    @cache_response(key_func = DefaultKeyConstructor(), timeout = 60 * 15)

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
    pagination_classes = LimitOffsetPagination

    @cache_response(key_func = DefaultKeyConstructor(), timeout = 60 * 15)
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
    pagination_classes = LimitOffsetPagination

    @cache_response(key_func = DefaultKeyConstructor(), timeout = 60 * 60 * 12)
    def retrieve(self, request, pk = None):
        author = get_object_or_404(Author,slug = pk)
        queryset = Novel.objects.filter(author = author)
        page = self.paginate_queryset(queryset)
        serializer = NovelInfoSerializer(page, many=True)
        finaldata = {'author':author.name,'results':serializer.data}
        return Response(finaldata)

