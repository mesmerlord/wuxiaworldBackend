from django.contrib import admin
from .models import (Announcement, Novel,Author,Category,Chapter,NovelViews, 
                    Tag, Profile, Bookmark, Settings, BlacklistPattern, Review, Report)

def repeat_scrape_on(modeladmin, request, queryset):
    queryset.update(repeatScrape=True)

def repeat_scrape_off(modeladmin, request, queryset):
    queryset.update(repeatScrape=False)

# Register your models here.
@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ["name", "repeatScrape", "created_at", "updated_at"]
    actions = [repeat_scrape_on,repeat_scrape_off]
    list_filter = ("source_novel__base_url", "repeatScrape","category")
    search_fields = ['name']

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["index", "novelParent", "created_at", "updated_at"]
    search_fields = ['novelParent__name' ]

@admin.register(NovelViews)
class NovelViewsAdmin(admin.ModelAdmin):
    def views_name(self,obj):
        queriedNovel = Novel.objects.filter(views = obj)
        if queriedNovel.count():
            return (queriedNovel.first().name)
        else:
            return obj.views
    list_display = ['views_name', "views", "created_at", "updated_at" ]
    search_fields = ['viewsNovelName']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ['reading_lists']
    search_fields = ['user__name']
    list_display = ["user","created_at", "updated_at"]

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    autocomplete_fields = ['novel', "chapter"]
    search_fields = ['novel__name']
    list_display = ['novel', "chapter", "profile_name", "created_at","updated_at"]
    def profile_name(self,obj):
        return Profile.objects.get(reading_lists = obj).user.first_name

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    autocomplete_fields = ['novel', 'owner_user', "last_read_chapter"]
    list_display = ['get_user', "title", "total_score", "last_read_chapter", 
                "novel"]
    def get_user(self,obj):
        return obj.owner_user.user

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', "novels_count", "created_at", "updated_at"]
    list_per_page = 1000

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', "novels_count","created_at", "updated_at"]
    list_per_page = 1000

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', "novels_count", "created_at", "updated_at"]

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    search_fields = ['profile__profile_owner']
    list_display = ['profile_name', "fontSize", "autoBookMark", "lowData",
                    "darkMode", "created_at", "updated_at"]
    def profile_name(self,obj):
        return obj.profile.user.first_name
        
@admin.register(BlacklistPattern)
class BlacklistPatternAdmin(admin.ModelAdmin):
    list_display = ['pattern', "enabled", "replacement"]

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', "description", "authored_by"]

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', "description", "reported_by", "chapter"]
    list_filter = ('title',)