from django.contrib import admin
from wuxiaworld.scraper.models import Source
# Register your models here.
@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ["source_novel", "created_at", "updated_at" ,"priority", "base_url"]
    list_filter = ("priority", "base_url")
    search_fields = ['source_novel__name']