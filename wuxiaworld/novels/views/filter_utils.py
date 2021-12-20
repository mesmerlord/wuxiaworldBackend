import django_filters
from wuxiaworld.novels.models import Novel

class NovelParamsFilter(django_filters.FilterSet):
    rating__gt = django_filters.NumberFilter(field_name='rating', lookup_expr='gt')
    rating__lt = django_filters.NumberFilter(field_name='rating', lookup_expr='lt')
    tag_name = django_filters.CharFilter(field_name='tag__slug', lookup_expr='iexact')
    category_name = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
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
