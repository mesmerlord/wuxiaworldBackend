from wuxiaworld.novels.serializers import (HomeNovelSerializer, SearchSerializer,
                     NovelSerializer, CatOrTagSerializer)
from wuxiaworld.novels.models import Novel, NovelViews
from rest_framework import viewsets, filters, pagination
from wuxiaworld.novels.permissions import ReadOnly
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework_extensions.cache.decorators import (
    cache_response
)
from django.db.models import Count
from wuxiaworld.novels.views.cache_utils import DefaultKeyConstructor, UserKeyConstructor
from wuxiaworld.novels.views.filter_utils import NovelParamsFilter

class SearchPagination(pagination.LimitOffsetPagination):       
    page_size = 6


class SearchSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.annotate(num_of_chaps = Count("chapter"))
    pagination_class = SearchPagination
    serializer_class = CatOrTagSerializer
    search_fields = ['name','slug']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = NovelParamsFilter

    @cache_response(key_func = DefaultKeyConstructor(), timeout = 60*15)
    def retrieve(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class NovelSerializerView(viewsets.ModelViewSet):
    permission_classes = (ReadOnly,)
    queryset = Novel.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = NovelParamsFilter
    serializer_class = NovelSerializer
    
    def get_serializer_class(self, *args, **kwargs):
        if self.action == "list":
            return CatOrTagSerializer
        else:
            return self.serializer_class
    def get_queryset(self):
        if self.action == "list":
            return super().get_queryset().select_related("views").prefetch_related(
            "category", "tag" )
        elif self.action == "retrieve":
            return super().get_queryset()

    @cache_response(key_func = UserKeyConstructor(), timeout = 60*60)
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        novelViews = NovelViews.objects.get(viewsNovelName = obj.slug)
        novelViews.updateViews()
        return super().retrieve(request, *args, **kwargs)

    @cache_response(key_func = DefaultKeyConstructor(), timeout = 60*60*2)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
