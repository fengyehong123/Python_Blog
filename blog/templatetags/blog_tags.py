from django import template
from ..models import Entry, Category, Tag

# 自定义标签

# 生成注册器,Django1.9版本之后才有的功能
register = template.Library()


@register.simple_tag
def get_recent_entries(num=5):

    # 获取所有的博客,根据创建时间倒序排序,然后切片前5条数据
    return Entry.objects.all().order_by('-created_time')[:num]


# 获取阅读量最多的5篇博客进行推荐
@register.simple_tag
def get_popular_entries(num=5):

    # 获取所有的博客,根据访问量倒序排序,然后切片前5条数据
    return Entry.objects.all().order_by('-visiting')[:num]


# 返回所有的分类
@register.simple_tag
def get_categories():
    return Category.objects.all()


# 获取当前分类下博客的数量
@register.simple_tag
def get_entry_count_of_category(category_name):

    # category__name : 有两个__下划线
    return Entry.objects.filter(category__name=category_name).count()


# 博客归档
@register.simple_tag
def archives():

    # 会返回一个列表,列表中的元素是每一篇文章创建的时间
    return Entry.objects.dates('created_time', 'month', order="DESC")


# 计算博客归档下有多少篇博客
@register.simple_tag
def get_entry_count_of_date(year, month):

    return Entry.objects.filter(created_time__year=year, created_time__month=month).count()


# 获取所有的标签
@register.simple_tag
def get_tags():
    return Tag.objects.all()


