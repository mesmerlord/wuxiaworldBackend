from django.urls import include, path

urlpatterns = [
    path("", include("wuxiaworld.novels.urls")),
] 