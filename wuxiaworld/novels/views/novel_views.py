from wuxiaworld.novels.serializers import SearchSerializer, NovelSerializer
from wuxiaworld.novels.models import Novel, NovelViews
from rest_framework import viewsets, filters, pagination
from wuxiaworld.novels.permissions import ReadOnly
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import django_filters
from rest_framework_extensions.cache.decorators import (
    cache_response
)
from django.db.models import Count
from wuxiaworld.novels.views.cache_utils import DefaultKeyConstructor


class SearchPagination(pagination.LimitOffsetPagination):       
    page_size = 6

class NovelParamsFilter(django_filters.FilterSet):
    rating__gt = django_filters.NumberFilter(field_name='rating', lookup_expr='gt')
    rating__lt = django_filters.NumberFilter(field_name='rating', lookup_expr='lt')
    tag_name = django_filters.CharFilter(field_name='tag__slug', lookup_expr='icontains')
    category_name = django_filters.CharFilter(field_name='category__slug', lookup_expr='icontains')
    numOfChaps__gt = django_filters.NumberFilter(field_name='numOfChaps', lookup_expr='gt')
    numOfChaps__lt = django_filters.NumberFilter(field_name='numOfChaps', lookup_expr='lt')
    order = django_filters.OrderingFilter(
        fields=(
            ('views__views', 'total_views'),('name','name'),
            ('created_at','created_at'),('numOfChaps','numOfChaps'),
            ('views__weeklyViews','weekly_views'),('views__monthlyViews','monthly_views'),
            ('views__yearlyViews','yearly_views'),('num_of_chaps','num_of_chaps'),
            ('rating','rating')
        ),

    )
    class Meta:
        model = Novel
        fields = ['rating', 'tag_name', 'category_name','numOfChaps']

class SearchSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.annotate(num_of_chaps = Count("chapter"))
    pagination_class = SearchPagination
    serializer_class = SearchSerializer
    search_fields = ['name','slug']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = NovelParamsFilter

    @cache_response(key_func = DefaultKeyConstructor(), timeout = 60*15)
    def retrieve(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class NovelSerializerView(viewsets.ModelViewSet):
    permission_classes = (ReadOnly,)
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = NovelParamsFilter
    
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        novelViews = NovelViews.objects.get(viewsNovelName = obj.slug)
        novelViews.updateViews()
        return super().retrieve(request, *args, **kwargs)

    @cache_response(key_func = DefaultKeyConstructor(), timeout = 60*15)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
