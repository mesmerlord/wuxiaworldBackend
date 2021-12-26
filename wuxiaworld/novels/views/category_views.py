from wuxiaworld.novels.serializers import (CategorySerializer, NovelSerializer,
                                TagSerializer, AuthorSerializer,NovelInfoSerializer,
                                CatOrTagSerializer, CategoryListSerializer, 
                                TagListSerializer, HomeNovelSerializer)
from wuxiaworld.novels.models import Novel, Category, Tag, Author
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
from wuxiaworld.novels.permissions import ReadOnly
from rest_framework.pagination import LimitOffsetPagination
from wuxiaworld.novels.views.cache_utils import (DefaultKeyConstructor, 
                    DummyConstructor)
from rest_framework_extensions.cache.decorators import (
    cache_response
)
from django.db.models import Count, Avg, Sum

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
        serializer = HomeNovelSerializer(page, many=True, context={'request': request})
        finaldata = {'category':category.name,'results':serializer.data,'count':queryset.count()}
        return Response(finaldata)
    
    @cache_response(key_func = DummyConstructor(), timeout = 60 * 60 * 24 * 7)
    def list(self, request):
        categories_by_views = self.queryset.annotate(
            avg_views = Avg('novel__views__views'),novel_count = Count('novel')
            ).order_by('-avg_views')
        category = categories_by_views.filter(
            novel_count__gt = 7
        )[:10]
        serializer = CategoryListSerializer(category,many=True,
                     context={'request': request})
        categories = CategorySerializer(categories_by_views, many = True)
        return Response({"categories":categories.data,"results":serializer.data})
        
class TagSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_classes = LimitOffsetPagination

    @cache_response(key_func = DefaultKeyConstructor(), timeout = 60 * 15)
    def retrieve(self, request, pk = None):
        tag = get_object_or_404(Tag,slug = pk)
        queryset = Novel.objects.filter(tag__slug = pk)
        page = self.paginate_queryset(queryset)
        serializer = NovelInfoSerializer(page, many=True,context={'request': request})
        finaldata = {'tag':tag.name,'results':serializer.data}
        return Response(finaldata)

    @cache_response(key_func = DummyConstructor(), timeout = 60 * 60 * 24 * 7)
    def list(self, request):
        tags_by_views = self.queryset.annotate(
            avg_views = Sum('novel__views__views')).order_by('-avg_views'
            ).annotate(
                novel_count = Count('novel'))
        tag = tags_by_views.filter(
            novel_count__gt = 7
        )[:5]
        serializer = TagListSerializer(tag,many=True, context={'request': request})
        tags = TagSerializer(tags_by_views,many=True)

        return Response({"tags":tags.data,"results":serializer.data})
        
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
        serializer = NovelInfoSerializer(page, many=True, 
                    context={'request': request})
        finaldata = {'author':author.name,'results':serializer.data}
        return Response(finaldata)

