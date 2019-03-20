from django.contrib import admin

# Register your models here.
from sites.models import DataType, Image, Link, Page, PageData, PageType, Site

admin.site.register(DataType)
admin.site.register(Image)
admin.site.register(Link)
admin.site.register(Page)
admin.site.register(PageData)
admin.site.register(PageType)
admin.site.register(Site)
