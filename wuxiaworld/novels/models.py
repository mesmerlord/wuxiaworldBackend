from django.db import models
from rest_framework import serializers
from django.utils.text import slugify
from django.utils.timezone import now
from .signals import *
from django.db.models import F
from django.contrib.auth.models import User


class Author(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField(max_length = 200, primary_key=True)
    def __str__(self):
        return self.name
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Author, self).save(*args, **kwargs)

class Category(models.Model):
    #Also used for language instead of creating a new model
    name = models.CharField(max_length = 200)
    slug = models.CharField(max_length = 200, blank = True)
    def __str__(self):
        return self.name
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.CharField(max_length = 200, blank = True)
    def __str__(self):
        return self.name
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

class NovelViews(models.Model):
    viewsNovelName = models.SlugField(max_length = 200, default = "",unique = True)
    views = models.IntegerField(default = 0)
    weeklyViews = models.IntegerField(default=0)
    monthlyViews = models.IntegerField(default=0)
    yearlyViews = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.viewsNovelName}"
    
    #Todo , this can cause deadlock/race condition later. Fix it using update function
    # instead
    def updateViews(self):
        obj = NovelViews.objects.filter(viewsNovelName = self.viewsNovelName)
        obj.update(views = F('views')+1 ,
                    weeklyViews = F('weeklyViews')+1,
                    monthlyViews = F('monthlyViews')+1 ,
                    yearlyViews = F('yearlyViews')+1)
        
class Novel(models.Model):
    SOURCE_CHOICES = [
        ('WuxSite', 'WuxSite'),
        ('ReadNovelFull', 'ReadNovelFull'),
        ('NovelFull', 'NovelFull'),
        ('WuxiaCo', 'WuxiaCo'),
        ('VipNovel', 'VipNovel'),
    ]

    name = models.CharField(max_length = 200)
    image = models.URLField(blank = True)
    imageThumb = models.URLField(blank = True)
    linkNU = models.URLField(blank = True)
    author = models.ForeignKey(Author, on_delete = models.CASCADE, null = True)
    category = models.ManyToManyField(Category, blank=True)
    tag = models.ManyToManyField(Tag, blank=True, default = None)
    description = models.TextField(blank = True)
    slug = models.SlugField(primary_key = True, default = None, max_length=200, blank = True)
    numOfChaps = models.IntegerField(default = 0)
    numOfTranslatedChaps = models.IntegerField(default = 0)
    novelStatus = models.BooleanField(default = True) #True will be for Ongoing, False for Completed
    viewsNovelName = models.ForeignKey(NovelViews,on_delete= models.CASCADE, blank=True, null=True)
    scrapeLink = models.CharField(max_length = 200,blank = True, default = "")
    repeatScrape = models.BooleanField(default = False)
    novelRef = models.CharField(max_length = 50, default = "", blank = True )
    sources = models.CharField(max_length = 100,choices=SOURCE_CHOICES,default = 'WuxSite')
    dateAdded = models.DateTimeField(default=now)
    def __str__(self):
        return self.name


class Chapter(models.Model):
    index = models.IntegerField(default = None, blank = True)
    text = models.TextField(max_length=None)
    title = models.TextField(max_length = 200)
    novelParent = models.ForeignKey(Novel, on_delete = models.CASCADE, verbose_name = "chapter")
    novSlugChapSlug = models.CharField( max_length = 200, blank = True, default = None)
    dateAdded = models.DateTimeField(default=now)
    scrapeLink = models.CharField(max_length = 200, blank = False)
    def save(self, *args, **kwargs):
        if not self.index:
            self.index = Chapter.objects.filter(novelParent = self.novelParent).count()+1
        
        if not self.novSlugChapSlug:
            self.novSlugChapSlug = f"{self.novelParent.slug}-{self.index}"
        super(Chapter, self).save(*args, **kwargs)
    def __str__(self):
        return f"Chapter {self.index} - {self.novelParent}"

class Bookmark(models.Model):
    last_read_novel = models.ForeignKey(Novel,on_delete=models.CASCADE)
    last_read_chapter = models.ForeignKey(Chapter,on_delete=models.CASCADE)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imageUrl = models.URLField(blank = True)
    reading_lists = models.ManyToManyField(Bookmark,blank = True)
