from django.db import models
from rest_framework import serializers
from django.utils.text import slugify
from django.utils.timezone import now
from .signals import *
from django.db.models import F, Sum
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime, ordinal
from datetime import timedelta
from wuxiaworld.custom_storages import (ThumbnailStorage, FullStorage, 
                        OriginalStorage)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now= True)
    class Meta:
        abstract = True

class Author(BaseModel):
    name = models.CharField(max_length = 200)
    slug = models.SlugField(max_length = 200, primary_key=True)
    def __str__(self):
        return self.name
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Author, self).save(*args, **kwargs)
    @property
    def novels_count(self):
        novels = Novel.objects.filter(author = self)
        return novels.count()

class Category(BaseModel):
    #Also used for language instead of creating a new model
    name = models.CharField(max_length = 200, unique=True)
    slug = models.CharField(max_length = 200, blank = True)
    def __str__(self):
        return self.name
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    @property
    def novels_count(self):
        novels = Novel.objects.filter(category = self)
        return novels.count()

    @property
    def views_count(self):
        novels = Novel.objects.filter(category = self)
        views = novels.aggregate(avg_views = Sum('views__views'))
        return views['avg_views']
    class Meta:
        ordering = ['name']
        
class Tag(BaseModel):
    name = models.CharField(max_length = 200, unique = True)
    slug = models.CharField(max_length = 200, blank = True)
    def __str__(self):
        return self.name
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)
    @property
    def novels_count(self):
        novels = Novel.objects.filter(tag = self)
        return novels.count()
    class Meta:
        ordering = ['name']

class NovelViews(BaseModel):
    viewsNovelName = models.SlugField(max_length = 200, default = "",unique = True)
    views = models.IntegerField(default = 0)
    weeklyViews = models.IntegerField(default=0)
    monthlyViews = models.IntegerField(default=0)
    yearlyViews = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.viewsNovelName}"
    
    #Todo , this can cause deadlock/race condition later. Fix it using update function
    # instead
    def updateViews(self, increment_num = 1):
        obj = NovelViews.objects.filter(viewsNovelName = self.viewsNovelName)
        obj.update(views = F('views')+increment_num ,
                    weeklyViews = F('weeklyViews')+increment_num,
                    monthlyViews = F('monthlyViews')+increment_num ,
                    yearlyViews = F('yearlyViews')+increment_num)
        
class Novel(BaseModel):
    name = models.CharField(max_length = 200)
    image = models.URLField(blank = True)
    imageThumb = models.URLField(blank = True)
    linkNU = models.URLField(blank = True)
    author = models.ForeignKey(Author, on_delete = models.CASCADE, null = True)
    category = models.ManyToManyField(Category, blank=True)
    tag = models.ManyToManyField(Tag, blank=True, default = None)
    description = models.TextField(blank = True)
    slug = models.SlugField(primary_key = True, default = None, max_length=200, blank = True, unique = True)
    numOfChaps = models.IntegerField(default = 0)
    novelStatus = models.BooleanField(default = True) #True will be for Ongoing, False for Completed
    views = models.ForeignKey(NovelViews,on_delete= models.CASCADE, blank=True, null=True)
    repeatScrape = models.BooleanField(default = False)
    last_chap_updated = models.DateTimeField(default = now)
    rating = models.DecimalField(blank = True, default = 5.0, max_digits = 3, decimal_places = 2)
    
    original_image = models.ImageField(storage=OriginalStorage(), blank = True,
                         null = True, max_length=500)
    new_image = models.ImageField(storage=FullStorage(), blank = True,
                             null = True, max_length=500)
    new_image_thumb = models.ImageField(storage=ThumbnailStorage(), blank = True,
                         null = True, max_length=500)

    def __str__(self):
        return self.name
    
    @property
    def review_count(self):
        reviews = Review.objects.filter(novel = self)
        return reviews.count()
    
    @property
    def human_date(self):
        reviews = Review.objects.filter(novel = self)
        return reviews.count()
    
    @property
    def chapter_count(self):
        chapters = Chapter.objects.filter(novelParent = self)
        return chapters.count()
    
    @property
    def ranking(self):
        rank = Novel.objects.order_by("-views__views").filter(views__views__gte = self.views.views)
        return ordinal(rank.count())
    
    @property
    def human_views(self):
        views = self.views.views
        num = float('{:.3g}'.format(views))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
    
class Chapter(BaseModel):
    index = models.IntegerField(default = None, blank = True)
    text = models.TextField(max_length=None)
    title = models.TextField(max_length = 200)
    novelParent = models.ForeignKey(Novel, on_delete = models.CASCADE, verbose_name = "chapter")
    novSlugChapSlug = models.CharField( max_length = 200, blank = True, default = None,
                db_index = True)
    scrapeLink = models.CharField(max_length = 200, blank = False)
    def save(self, *args, **kwargs):
        if not self.index:
            self.index = Chapter.objects.filter(novelParent = self.novelParent).count()+1
        
        if not self.novSlugChapSlug:
            self.novSlugChapSlug = f"{self.novelParent.slug}-{self.index}"
        super(Chapter, self).save(*args, **kwargs)
    def __str__(self):
        return f"Chapter {self.index} - {self.novelParent}"
    
    @property
    def get_human_time(self):
        chapAddedTime = self.created_at
        dayAgo = now() + timedelta(hours = -24)
        if chapAddedTime < dayAgo:
            return chapAddedTime.strftime('%B %-d %Y')
        else:
            return naturaltime(chapAddedTime)

class Bookmark(BaseModel):
    novel = models.ForeignKey(Novel, on_delete = models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete = models.CASCADE, null=True)

    def __str__(self):
        return self.novel.name

class Settings(BaseModel):
    fontSize = models.IntegerField(default = 20)
    autoBookMark = models.BooleanField(default = True)
    lowData = models.BooleanField(default = False)
    darkMode = models.BooleanField(default = False)

    
class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_owner')
    imageUrl = models.URLField(blank = True)
    reading_lists = models.ManyToManyField(Bookmark, blank = True)
    settings = models.OneToOneField(Settings, on_delete = models.DO_NOTHING,
                         null=True, default = None, blank = True)
    
    def __str__(self):
        return self.user.first_name

class BlacklistPattern(BaseModel):
    pattern = models.TextField(max_length = 100,blank = True, null = True)
    enabled = models.BooleanField(default = True)
    replacement = models.TextField(max_length = 100,blank = True, null = True,
                    default = "")

class Review(BaseModel):
    title = models.CharField(max_length = 100, default = "N/A")
    description = models.TextField(blank = True, null = True)
    total_score = models.IntegerField(default = 5,
                 validators=[MinValueValidator(1), MaxValueValidator(5)])
    last_read_chapter = models.ForeignKey(Chapter, on_delete=models.DO_NOTHING,
                    null=True, blank = True)
    owner_user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    novel = models.ForeignKey(Novel,on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('novel', 'owner_user',)

class Announcement(BaseModel):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    published = models.BooleanField(default = True)
    authored_by = models.ForeignKey(Profile, on_delete=models.CASCADE)

class Report(BaseModel):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    reported_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null = True, blank = True)
    checked = models.BooleanField(default = False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null = True, blank = True)

    class Meta:
        unique_together = ('reported_by', 'chapter', "description")
