from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path,re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from wuxiaworld.novels.views import (deleteDuplicate, deleteUnordered, addNovels,siteMap)
from wuxiaworld.novels.views import (GoogleLogin, home)

urlpatterns = [
    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(settings.ADMIN_URL, admin.site.urls),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("wuxiaworld.novels.api_router")),
    # DRF auth token
    path("upload/novels", addNovels),
    path("utils/deleteDupe", deleteDuplicate),
    path("utils/deleteUnordered", deleteUnordered),
    path("utils/sitemap/<site>", siteMap),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    
]
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [re_path(r'.*', home)]

if settings.DEBUG:

    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
