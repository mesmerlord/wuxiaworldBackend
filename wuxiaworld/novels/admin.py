from django.contrib import admin
from .models import (Novel,Author,Category,Chapter,NovelViews, 
                    Tag, Profile, Bookmark, Settings, BlacklistPattern)

def repeat_scrape_on(modeladmin, request, queryset):
    queryset.update(repeatScrape=True)

def repeat_scrape_off(modeladmin, request, queryset):
    queryset.update(repeatScrape=False)

# Register your models here.
@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ["name", "repeatScrape", "dateAdded"]
    actions = [repeat_scrape_on,repeat_scrape_off]
    list_filter = ("sources", "repeatScrape",)
    search_fields = ['name']

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["index", "novelParent", "dateAdded"]
    search_fields = ['novelParent__name']

@admin.register(NovelViews)
class NovelViewsAdmin(admin.ModelAdmin):
    def views_name(self,obj):
        queriedNovel = Novel.objects.filter(viewsNovelName = obj)
        if queriedNovel.count():
            return (queriedNovel.first().name)
        else:
            return obj.viewsNovelName
    list_display = ['views_name', "views" ]
    search_fields = ['viewsNovelName']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ['reading_lists']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    autocomplete_fields = ['novel', "chapter"]
    search_fields = ['novel___name']

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Settings)
admin.site.register(BlacklistPattern)

    


