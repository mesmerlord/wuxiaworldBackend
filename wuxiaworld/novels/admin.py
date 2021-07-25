from django.contrib import admin
from .models import Novel,Author,Category,Chapter

# Register your models here.
admin.site.register(Novel)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Chapter)