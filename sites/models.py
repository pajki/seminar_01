# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DataType(models.Model):
    code = models.CharField(primary_key=True, max_length=20)

    class Meta:
        db_table = 'data_type'


class Image(models.Model):
    page = models.ForeignKey('Page', models.DO_NOTHING, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=50, blank=True, null=True)
    data = models.BinaryField(blank=True, null=True)
    accessed_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'image'


class Link(models.Model):
    from_page = models.ForeignKey('Page', models.DO_NOTHING, db_column='from_page', primary_key=True, related_name='from_page')
    to_page = models.ForeignKey('Page', models.DO_NOTHING, db_column='to_page', related_name='to_page')

    class Meta:
        db_table = 'link'
        unique_together = (('from_page', 'to_page'),)


class Page(models.Model):
    site = models.ForeignKey('Site', models.DO_NOTHING, blank=True, null=True)
    page_type_code = models.ForeignKey('PageType', models.DO_NOTHING, db_column='page_type_code', blank=True, null=True)
    url = models.CharField(unique=True, max_length=3000, blank=True, null=True)
    html_content = models.TextField(blank=True, null=True)
    http_status_code = models.IntegerField(blank=True, null=True)
    accessed_time = models.DateTimeField(blank=True, null=True)
    crawl_delay = models.IntegerField(default=4)

    class Meta:
        db_table = 'page'


class PageData(models.Model):
    page = models.ForeignKey(Page, models.DO_NOTHING, blank=True, null=True)
    data_type_code = models.ForeignKey(DataType, models.DO_NOTHING, db_column='data_type_code', blank=True, null=True)
    data = models.BinaryField(blank=True, null=True)

    class Meta:
        db_table = 'page_data'


class PageType(models.Model):
    code = models.CharField(primary_key=True, max_length=20)

    class Meta:
        db_table = 'page_type'


class Site(models.Model):
    domain = models.CharField(max_length=500, blank=True, null=True)
    robots_content = models.TextField(blank=True, null=True)
    sitemap_content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'site'
