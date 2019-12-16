from django.contrib import admin
from . import models


# 博客模型定义要展示的字段数据
class EntryAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "visiting", "modified_time", "created_time"]


# 把我们的数据模型注册到后台的管理界面
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Entry, EntryAdmin)
