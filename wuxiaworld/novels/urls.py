from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path,re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from wuxiaworld.novels.views.util_views import return_robots
from wuxiaworld.novels.views.views import (deleteDuplicate, deleteUnordered, addNovels,siteMap,
            addSources, replace_images)
from wuxiaworld.novels.views.views import (GoogleLogin, FacebookLogin)

urlpatterns = [
    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),

    path(settings.ADMIN_URL, admin.site.urls),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()
    
else:
    urlpatterns += [path("", return_robots, name = "home"),]
# API URLS
urlpatterns += [
    # API base url
    path("robots.txt", return_robots),
    path("api/", include("wuxiaworld.novels.api_router")),
    # DRF auth token
    path("upload/novels", addNovels),
    path("upload/sources", addSources),
    path("utils/deleteDupe", deleteDuplicate),
    path("utils/deleteUnordered", deleteUnordered),
    path("utils/sitemap/<site>", siteMap),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('rest-auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path("utils/replace_images", replace_images),

]
# if not settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

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
