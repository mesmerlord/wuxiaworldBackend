from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views.views import (NovelSerializerView, CategorySerializerView, 
                AuthorSerializerView, ChaptersSerializerView,SingleChapterSerializerView,
                SearchSerializerView, ProfileSerializerView, TagSerializerView, 
                BookmarkSerializerView, SettingsSerializerView, ReportSerializerView,
                AnnouncementSerializerView, ReviewSerializerView,
                GetAllNovelSerializerView)
from wuxiaworld.novels.views.home_views import (HomeSerializerView,
             LatestChaptersSerializerView, )
from wuxiaworld.novels.views.recommendation_views import (RecommendationSerializerView)
from django.urls import include, path,re_path

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('novels', NovelSerializerView)
router.register('admin-novels', GetAllNovelSerializerView)
router.register('categories', CategorySerializerView)
router.register('tags', TagSerializerView)
router.register('author', AuthorSerializerView)
router.register('getchapter', SingleChapterSerializerView)
router.register('chapters', ChaptersSerializerView)
router.register('search', SearchSerializerView)
router.register('users', ProfileSerializerView)
router.register('bookmark', BookmarkSerializerView)
router.register('settings', SettingsSerializerView)
router.register('report', ReportSerializerView)
router.register('announcements', AnnouncementSerializerView)
router.register('review', ReviewSerializerView)

app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    path('home_view/', HomeSerializerView.as_view()),
    path('latest_chapters/', LatestChaptersSerializerView.as_view()),
    path('recommendations/<pk>', RecommendationSerializerView.as_view()),
            
            ]
