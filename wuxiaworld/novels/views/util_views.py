from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from wuxiaworld.novels.tasks import (add_novels, add_sources, delete_dupes,
                     delete_unordered_chapters )

from django.http import HttpResponse
from ..models import Novel

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

def addNovels(request):
    add_novels.delay()
    return HttpResponse("<li>Done</li>")

def addSources(request):
    add_sources.delay()
    return HttpResponse("<li>Done</li>")

def deleteDuplicate(request):
    delete_dupes.delay()
    return HttpResponse("<li>Done</li>")

def deleteUnordered(request):
    delete_unordered_chapters.delay()
    return HttpResponse("<li>Done</li>")

def siteMap(request, *args,**kwargs):
    allNovels = Novel.objects.values_list('slug', 'created_at').all()
    siteName = kwargs['site'].split("-")
    top = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    bottom = "</urlset>"
    sitemap = top+"\n".join([f"<url><loc>https://www.{siteName[0]}.{siteName[1]}/novel/{x[0]}</loc><lastmod>{x[1].date()}</lastmod></url>" \
                for x in allNovels]) + bottom
    return HttpResponse(sitemap, content_type='text/xml')
