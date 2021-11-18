from rest_framework import serializers
from .models import Novel,Category,Author,Chapter, NovelViews, Tag, Profile, Bookmark, Settings
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
       
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
       
class ChapterSerializer(serializers.ModelSerializer):
    novelParentName = serializers.CharField(source='novelParent.name')
    nextChap = serializers.SerializerMethodField(method_name = "get_next_chap")
    prevChap = serializers.SerializerMethodField(method_name = "get_prev_chap")

    class Meta:
        model = Chapter
        lookup_field = "novSlugChapSlug"
        fields = ('index','title',"text", "nextChap","novelParent","novelParentName", "prevChap")
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
    views = serializers.CharField(source = "viewsNovelName.views")    
    tag = TagSerializer(many= True)
    chapters = serializers.SerializerMethodField(method_name = "get_chapters")

    class Meta:
        model = Novel
        # fields = ('category','name', 'image','slug','author','description','views_set',)
        exclude = ('viewsNovelName','repeatScrape')
        # fields = '__all__'
    def get_chapters(self,obj):
        chapter = Chapter.objects.filter(novelParent = obj)
        return chapter.count()

class NovelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        fields = ('name', 'image', 'slug', )

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