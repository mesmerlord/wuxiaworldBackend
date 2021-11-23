from wuxiaworld.novels.serializers import SearchSerializer, NovelSerializer
from wuxiaworld.novels.models import Novel, NovelViews
from rest_framework import viewsets, filters, pagination
from wuxiaworld.novels.permissions import ReadOnly

class SearchPagination(pagination.LimitOffsetPagination):       
    page_size = 6

class SearchSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.all()
    pagination_class = SearchPagination
    serializer_class = SearchSerializer
    search_fields = ['name','slug']
    filter_backends = (filters.SearchFilter,)

class NovelSerializerView(viewsets.ModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        novelViews = NovelViews.objects.get(viewsNovelName = obj.slug)
        novelViews.updateViews()
        
        return super().retrieve(request, *args, **kwargs)
