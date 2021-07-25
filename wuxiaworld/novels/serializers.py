from rest_framework import serializers
from .models import Novel,Category,Author,Chapter
from rest_framework.pagination import PageNumberPagination


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        # fields = ('name', 'catSlug')
class ChapterSerializer(serializers.ModelSerializer):
    novelParentName = serializers.CharField(source='novelParent.name')
    class Meta:
        model = Chapter
        lookup_field = "novSlugChapSlug"
        fields = ('index','title',"text", "nextChap","novelParent","novelParentName")

class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Author
        fields = ('name', 'slug')

class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        fields = ('name', 'slug')

class ChaptersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chapter
        fields = ('index','title',"novSlugChapSlug")

class NovelSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = CategorySerializer(many = True)

    class Meta:
        model = Novel
        # fields = ('name', 'image','slug','author','description')
        
        fields = '__all__'
    

class NovelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        
        fields = ('name', 'image', 'description','slug')