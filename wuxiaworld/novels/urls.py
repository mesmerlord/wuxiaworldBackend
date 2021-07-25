from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path, include,re_path
from django.contrib.auth.models import User
from rest_framework import routers
from .models import Novel
from django.conf.urls.static import static

from .views import (NovelSerializerView, CategorySerializerView, 
                AuthorSerializerView, ChaptersSerializerView, catUpload,
                novelUpload,chapUpload,SingleChapterSerializerView,SearchSerializerView )


router = routers.DefaultRouter()
router.register('novels', NovelSerializerView)
router.register('categories', CategorySerializerView)
router.register('author', AuthorSerializerView)
router.register('getchapter', SingleChapterSerializerView)
router.register('chapters', ChaptersSerializerView)
router.register('search', SearchSerializerView)



urlpatterns = [
    path('hello/', admin.site.urls),
    path('', include(router.urls)),
    path("upload/category", catUpload),
    path("upload/novels", novelUpload),
    path("upload/chapters", chapUpload),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]