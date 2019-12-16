from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings
from blog.feed import LatestEntriesFeed
from blog import views as blog_views
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from blog.models import Entry


info_dict = {
    # 所有的博客都要放到站点地图当中
    'queryset': Entry.objects.all(),
    # modified_time 根据这个字段来调整站点地图的修改日期
    'date_field': 'modified_time'
}


urlpatterns = [
    # 当直接访问用户的根路由时,显示首页
    url(r'^$', blog_views.index),
    url(r'^admin/', admin.site.urls),
    # 设置二级路由,以blog开头的路由,分发到url路由文件中
    url(r'^blog/', include('blog.urls')),
    url(r'^login/$', blog_views.login),
    url(r'^latest/feed/$', LatestEntriesFeed()),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {'blog': GenericSitemap(info_dict, priority=0.6)}},
        # 提供url反向解析
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^logout/$', blog_views.logout),
    # 设置评论的url,评论插件要求url这么设置
    url(r'^comments/', include('django_comments.urls')),

    # 给静态图片文件添加访问的路径
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 自定义的错误页面处理
handler403 = blog_views.permission_denied
handler404 = blog_views.page_not_found
handler500 = blog_views.page_error
