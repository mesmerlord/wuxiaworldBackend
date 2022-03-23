from rest_framework import serializers
from .models import (Announcement, Novel,Category,Author,Chapter, NovelViews,
                 Review, Tag, Profile, Bookmark, Settings, Review, Report )
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('created_at','updated_at', "id")
        ordering = ['name']
       
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ('created_at','updated_at')
        ordering = ['name']
       
class ChapterSerializer(serializers.ModelSerializer):
    novelParentName = serializers.CharField(source='novelParent.name')
    nextChap = serializers.SerializerMethodField(method_name = "get_next_chap")
    prevChap = serializers.SerializerMethodField(method_name = "get_prev_chap")

    class Meta:
        model = Chapter
        lookup_field = "novSlugChapSlug"
        fields = ('index','title',"text", "nextChap","novelParent","novelParentName", "prevChap", "id")
    def get_next_chap(self,obj):
        nextChap = Chapter.objects.filter(novelParent = obj.novelParent, index__gt = obj.index )
        if nextChap:
            return nextChap.order_by('index').first().index
        else:
            return None
    def get_prev_chap(self,obj):
        prevChap = Chapter.objects.filter(novelParent = obj.novelParent, index__lt = obj.index )
        if prevChap:
            return prevChap.order_by('-index').first().index

        else:
            return None
class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Author
        fields = ('name', 'slug')

class SearchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Novel
        fields = ('name', 'slug','imageThumb', 'image','description')

class ChaptersSerializer(serializers.ModelSerializer):
    timeAdded = serializers.SerializerMethodField(method_name = "get_time")

    class Meta:
        model = Chapter
        fields = ('index','title',"novSlugChapSlug",'timeAdded')
    def get_time(self,obj):
        chapAddedTime = obj.created_at
        dayAgo = now() + timedelta(hours = -24)
        if chapAddedTime < dayAgo:
            return chapAddedTime.strftime('%B %-d %Y')
        else:
            return naturaltime(chapAddedTime)
        

class NovelViewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = NovelViews
        fields = '__all__'

class NovelSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = CategorySerializer(many= True)
    views = serializers.CharField(source = "views.views")    
    tag = TagSerializer(many= True)
    chapters = serializers.SerializerMethodField(method_name = "get_chapters")
    review_count = serializers.IntegerField()    
    image = serializers.ImageField(use_url=True, source = "new_image")
    imageThumb = serializers.ImageField(use_url=True, source = "new_image_thumb")
    first_chapter = serializers.SerializerMethodField(method_name = "get_first_chapter")

    class Meta:
        model = Novel
        # fields = ('category','name', 'image','slug','author','description','views_set',)
        exclude = ('repeatScrape',)
        # fields = '__all__'
    def get_chapters(self,obj):
        chapter = Chapter.objects.filter(novelParent = obj)
        return chapter.count()
    def get_first_chapter(self,obj):
        chapter = Chapter.objects.filter(novelParent = obj).order_by("index").first()
        if chapter:
            return chapter.novSlugChapSlug
        else:
            return None

class NovelInfoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, source = "new_image")
    # imageThumb = serializers.ImageField(use_url=True, source = "new_image_thumb")
    class Meta:
        model = Novel
        fields = ('name', 'image', 'slug')

class LoggedNovelInfoSerializer(serializers.ModelSerializer):
    bookmarked = serializers.SerializerMethodField(method_name = "get_bookmark")
    class Meta:
        model = Novel
        fields = ('name', 'image', 'description','slug','bookmarked')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", 'last_name', 'username', 'email')

class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    initials = serializers.SerializerMethodField(method_name = "get_initials")
    user = UserSerializer(read_only=True)
    settings = SettingsSerializer()
    class Meta:
        model = Profile
        fields = ('user', 'imageUrl','initials', 'settings' )
    
    def get_initials(self,obj):
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        if first_name and last_name:
            return f"{first_name[0]}{last_name[0]}"
        else:
            return None
class BookmarkSerializer(serializers.ModelSerializer):
    # novSlugChapSlug = serializers.CharField(source = "chapter.novSlugChapSlug", allow_null=True)
    last_read = serializers.SerializerMethodField(method_name = "get_last_read")
    last_chapter = serializers.SerializerMethodField(method_name = "get_last_chapter")
    next_chapter = serializers.SerializerMethodField(method_name = "get_next_chapter")

    novelInfo = NovelInfoSerializer(source = "novel")
    class Meta:
        model = Bookmark
        fields = ("last_read","last_chapter", "next_chapter", "created_at", "id", "novelInfo")

    def get_last_read(self,obj):
        if obj.chapter:
            return ChaptersSerializer(obj.chapter).data
        elif obj.novel:
            data = Chapter.objects.filter(novelParent = obj.novel).order_by('index')
            if data:
                return ChaptersSerializer(data.first()).data
            else:
                return None
    def get_next_chapter(self,obj):
        if obj.chapter:
            chapter = Chapter.objects.filter(novelParent = obj.chapter.novelParent
                        , index__gt = obj.chapter.index).order_by('index')
            if chapter:
                return ChaptersSerializer(chapter.first()).data
            else:
                return None
        else:
            return None

    def get_last_chapter(self,obj):
        lastChapter = None
        if obj.chapter:
            lastChapter = Chapter.objects.filter(novelParent = obj.chapter.novelParent).order_by('-index').first()
        elif obj.novel:
            lastChapter = Chapter.objects.filter(novelParent = obj.novel).order_by('-index').first() 
        if lastChapter:
            return ChaptersSerializer(lastChapter).data
        else:
            return None

class UpdateBookmarkSerializer(serializers.ModelSerializer):
    last_read = serializers.SerializerMethodField(method_name = "get_last_read")
    def get_last_read(self,obj):
        if obj.chapter:
            return ChaptersSerializer(obj.chapter).data
        elif obj.novel:
            data = Chapter.objects.filter(novelParent = obj.novel).order_by('index')
            if data:
                return ChaptersSerializer(data.first()).data
            else:
                return None
    class Meta:
        model = Bookmark
        fields = ("last_read", "created_at", "id")

class HomeNovelSerializer(serializers.ModelSerializer):
    views = serializers.CharField(source = "human_views")
    chapters = serializers.CharField(source = "chapter_count")
    image = serializers.ImageField(use_url=True, source = "new_image")
    # imageThumb = serializers.ImageField(use_url=True, source = "new_image_thumb")

    class Meta:
        model = Novel
        fields = ('name', 'image','slug',"rating", "ranking", "views", "chapters",
        )
    
class HomeSerializer(serializers.ModelSerializer):
    # views_count = serializers.CharField()
    novels = serializers.SerializerMethodField(source = "get_novels")

    class Meta:
        model = Category
        exclude = ('created_at','updated_at', "id")
    def get_novels(self,obj):
        novels = Novel.objects.filter(category = obj).order_by("-views__views")[:8]
        return HomeNovelSerializer(novels, many = True, 
        context={'request': self.context['request']}).data

class LatestChapterSerializer(serializers.ModelSerializer):
    novel_name = serializers.CharField(source = "novelParent.name")
    novel_thumb = serializers.ImageField(use_url=True,
                 source = "novelParent.new_image_thumb")
    created_at = serializers.CharField(source = "get_human_time")
    class Meta:
        model = Chapter
        exclude = ("text",'updated_at', "id","scrapeLink")
    # def get_novel_thumb(self,obj):
    #     if obj.novelParent.new_image_thumb:
    #         request = self.context.get("request")
    #         return request.build_absolute_uri(obj.novelParent.new_image_thumb.url)
    #     else:
    #         return None
class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"

class ReportSerializer(serializers.ModelSerializer):
    checked = serializers.CharField(read_only = True)
    class Meta:
        model = Report
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"

class CatOrTagSerializer(serializers.ModelSerializer):
    views = serializers.CharField(source = "human_views")
    chapters = serializers.CharField(source = "chapter_count")
    category = CategorySerializer(many = True)
    tag = TagSerializer(many = True)
    image = serializers.ImageField(use_url=True, source = "new_image")
    imageThumb = serializers.ImageField(use_url=True, source = "new_image_thumb")

    class Meta:
        model = Novel
        fields = ('name', 'image','slug','description', "rating", "ranking", "views", "chapters",
        "imageThumb", "category", "tag")
    
class CategoryListSerializer(serializers.ModelSerializer):
    novels = serializers.SerializerMethodField(source = "get_novels")
    class Meta:
        model = Category
        exclude = ('created_at','updated_at', "id")
    def get_novels(self,obj):
        novels = Novel.objects.filter(category = obj).order_by("-views__views")[:4]
        return HomeNovelSerializer(novels, many = True).data
    
class TagListSerializer(serializers.ModelSerializer):
    novels = serializers.SerializerMethodField(source = "get_novels")
    class Meta:
        model = Tag
        exclude = ('created_at','updated_at', "id")
    def get_novels(self,obj):
        novels = Novel.objects.filter(tag = obj).order_by("-views__views")[:4]
        return HomeNovelSerializer(novels, many = True,
                context={'request': self.context['request']}).data

class AllNovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        fields = ("slug",)
