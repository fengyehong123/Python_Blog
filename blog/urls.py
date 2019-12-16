from django.conf.urls import url
from . import views


# 给blog提供一个命名空间
app_name = "blog"

urlpatterns = [
    # 当访问blog首页的时候,经过这个路由
    url(r'^$', views.index, name='blog_index'),
    # 正则匹配,只匹配数字
    url(r'^(?P<blog_id>[0-9]+)/$', views.detail, name='blog_detail'),
    # /category/23
    url(r'^category/(?P<category_id>[0-9]+)/$', views.category, name='blog_category'),
    url(r'^tag/(?P<tag_id>[0-9]+)/$', views.tag, name='blog_tag'),
    # 进行博客的搜索
    url(r'^search/$', views.search, name='blog_search'),
    url(r'^archives/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', views.archives, name='blog_archives'),
    url(r'^reply/(?P<comment_id>\d+)/$', views.reply, name='comment_reply'),
]


