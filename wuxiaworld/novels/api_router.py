from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (NovelSerializerView, CategorySerializerView, 
                AuthorSerializerView, ChaptersSerializerView,SingleChapterSerializerView,
                SearchSerializerView, ProfileSerializerView, TagSerializerView, 
                BookmarkSerializerView, SettingsSerializerView )


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('novels', NovelSerializerView)
router.register('categories', CategorySerializerView)
router.register('tags', TagSerializerView)
router.register('author', AuthorSerializerView)
router.register('getchapter', SingleChapterSerializerView)
router.register('chapters', ChaptersSerializerView)
router.register('search', SearchSerializerView)
router.register('users', ProfileSerializerView)
router.register('bookmark', BookmarkSerializerView)
router.register('settings', SettingsSerializerView)

app_name = "api"
urlpatterns = router.urls