from wuxiaworld.novels.serializers import NovelInfoSerializer, HomeNovelSerializer
from wuxiaworld.novels.permissions import ReadOnly
from rest_framework import filters
from rest_framework_extensions.cache.decorators import (
    cache_response
)
from rest_framework.generics import RetrieveAPIView
from wuxiaworld.novels.models import Novel, Tag
from rest_framework.response import Response
from wuxiaworld.novels.views.cache_utils import UserKeyConstructor

class RecommendationSerializerView(RetrieveAPIView):
    permission_classes = [ReadOnly]
    queryset = Novel.objects.all()

    @cache_response(key_func = UserKeyConstructor(), timeout = 60*60)
    def retrieve(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        random_tag = Tag.objects.filter(novel = obj).order_by('?').first()
        novels = Novel.objects.filter(tag = random_tag).order_by(
            "-views__views").exclude(slug=obj.slug)[:16]
        serializer = HomeNovelSerializer(novels, 
                many=True,context={'request': request})
        return Response({"results":serializer.data, "tag": random_tag.name,
            'novel':obj.name})
