from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from wuxiaworld.users.api.views import UserViewSet
from wuxiaworld.novels.views import (NovelSerializerView, CategorySerializerView, 
                AuthorSerializerView, ChaptersSerializerView,SingleChapterSerializerView,SearchSerializerView )


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register('novels', NovelSerializerView)
router.register('categories', CategorySerializerView)
router.register('author', AuthorSerializerView)
router.register('getchapter', SingleChapterSerializerView)
router.register('chapters', ChaptersSerializerView)
router.register('search', SearchSerializerView)

app_name = "api"
urlpatterns = router.urls
