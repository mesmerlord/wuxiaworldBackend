from rest_framework import serializers
from .models import Novel,Category,Author,Chapter, NovelViews, Tag, Profile
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
        chapAddedTime = obj.dateAdded
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
        exclude = ('viewsNovelName', 'scrapeLink','sources','repeatScrape')
        # fields = '__all__'
    def get_chapters(self,obj):
        chapter = Chapter.objects.filter(novelParent = obj)
        return chapter.count()

class NovelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        
        fields = ('name', 'image', 'description','slug')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", 'last_name', 'username', 'email')

class ProfileSerializer(serializers.ModelSerializer):
    initials = serializers.SerializerMethodField(method_name = "get_initials")
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ('user', 'imageUrl','initials' )
    
    def get_initials(self,obj):
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        if first_name and last_name:
            return f"{first_name[0]}{last_name[0]}"
        else:
            return None
        