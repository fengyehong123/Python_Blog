import json
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.conf import settings
from . import models
import markdown
import pygments
# 导入Django的分页功能
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django_comments.models import Comment
from django_comments import models as comment_models


def index(request):

    # 获取所有的博客文章
    entries = models.Entry.objects.all()
    # 有值使用给定的值,默认使用1
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    # 获取分页对象
    page_date = pagination_data(paginator, page)

    # locals() 把当前所有的变量打包成字典传输进去,把entries变量传输到前端
    return render(request, 'blog/index.html', locals())


# blog_id 从前端接收的参数
def detail(request, blog_id):

    # entry = models.Entry.objects.get(id=blog_id)

    # 如果根据id能获取出对象,就进行获取,获取不到就返回404界面
    entry = get_object_or_404(models.Entry, id=blog_id)

    # 通过markdown把数据渲染成html的格式
    # 初始化markdown对象
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        # 支持博客内容高亮,配合pygments使用
        'markdown.extensions.codehilite',
        # 支持博客生成目录
        'markdown.extensions.toc',
    ])

    # 把markdown格式的数据转化为html格式的数据
    entry.body = md.convert(entry.body)
    # 为markdown格式的数据增加目录
    entry.toc = md.toc

    # 调用模型中的方法,增加文章的访问量
    entry.increase_visiting()

    # 博客所关联的所有的评论,都放在此列表当中
    comment_list = list()

    def get_comment_list(comments):
        for comment in comments:
            comment_list.append(comment)

            children = comment.child_comment.all()
            # 如果一个评论还有子评论的话,就递归调用获取所有的评论
            if len(children) > 0:
                get_comment_list(children)

    # 获取出所有的顶级父评论
    """参数一:关联的博客的id,参数二:父评论,参数三:评论内容所关联的app的标签
       根据提交的时间进行排序
    """
    top_comments = Comment.objects.filter(object_pk=blog_id,
                                          parent_comment=None,
                                          content_type__app_label='blog'
                                          ).order_by('-submit_date')

    get_comment_list(top_comments)

    # locals() 函数会以字典类型返回当前位置的全部局部变量。
    return render(request, 'blog/detail.html', locals())


# 博客的分页
def make_paginator(objects, page, num=5):
    # Django提供的分页对象,参数1:需要被分页的对象,参数2:每页显示的博客数量
    paginator = Paginator(objects, num)
    try:
        object_list = paginator.page(page)
    # 如果请求的页码不是整数
    except PageNotAnInteger:
        # 显示第一页
        object_list = paginator.page(1)
    # 如果请求的页码不存在
    except EmptyPage:
        # 直接显示最后一页
        object_list = paginator.page(paginator.num_pages)
    # 返回查询到的数据和分页器
    return object_list, paginator


# 博客分类的查询
def category(request, category_id):
    # 根据分类的id查询分类
    # cate = models.Category.objects.get(id=category_id)

    cate = get_object_or_404(models.Category, id=category_id)
    # 根据分类查询,该分类下的文章
    entries = models.Entry.objects.filter(category=cate)
    # 分类下的文章也可能有很多,需要进行分类
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    # 获取分页对象
    page_date = pagination_data(paginator, page)

    return render(request, 'blog/index.html', locals())


def tag(request, tag_id):
    """博客标签的查询"""

    # tg = models.Tag.objects.get(id=tag_id)
    tg = get_object_or_404(models.Tag, id=tag_id)
    if tg == "全部":
        entries = models.Entry.objects.all()
    else:
        entries = models.Entry.objects.filter(tags=tag_id)
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    # 获取分页对象
    page_date = pagination_data(paginator, page)

    return render(request, 'blog/index.html', locals())


def search(request):
    """博客的搜索"""
    # 根基keyword关键字进行搜索,如果没有关键字的话,就使用none
    keyword = request.GET.get('keyword', None)
    if not keyword:
        error_msg = "请输入关键字"
        return render(request, 'blog/index.html', locals())

    # 如果有关键字的话,需要搜索文章的标题,摘要,正文
    entries = models.Entry.objects.filter(Q(title__icontains=keyword) | Q(body__icontains=keyword)
                                          | Q(abstract__icontains=keyword))

    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    # 获取分页对象
    page_date = pagination_data(paginator, page)

    return render(request, 'blog/index.html', locals())


def pagination_data(paginator, page):
    """
    用于自定义展示分页页码的方法
    :param paginator: Paginator类的对象
    :param page: 当前请求的页码
    :return: 一个包含所有页码和符号的字典
    """
    if paginator.num_pages == 1:
        # 如果无法分页，也就是只有1页不到的内容，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
        return {}
    # 当前页左边连续的页码号，初始值为空
    left = []

    # 当前页右边连续的页码号，初始值为空
    right = []

    # 标示第 1 页页码后是否需要显示省略号
    left_has_more = False

    # 标示最后一页页码前是否需要显示省略号
    right_has_more = False

    # 标示是否需要显示第 1 页的页码号。
    # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
    # 其它情况下第一页的页码是始终需要显示的。
    # 初始值为 False
    first = False

    # 标示是否需要显示最后一页的页码号。
    # 需要此指示变量的理由和上面相同。
    last = False

    # 获得用户当前请求的页码号
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    except:
        page_number = 1

    # 获得分页后的总页数
    total_pages = paginator.num_pages

    # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
    page_range = paginator.page_range

    if page_number == 1:
        # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
        # 此时只要获取当前页右边的连续页码号，
        # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
        # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
        right = page_range[page_number:page_number + 4]

        # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
        # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
        if right[-1] < total_pages - 1:
            right_has_more = True

        # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
        # 所以需要显示最后一页的页码号，通过 last 来指示
        if right[-1] < total_pages:
            last = True

    elif page_number == total_pages:
        # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
        # 此时只要获取当前页左边的连续页码号。
        # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
        # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
        left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

        # 如果最左边的页码号比第 2 页页码号还大，
        # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
        if left[0] > 2:
            left_has_more = True

        # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
        # 所以需要显示第一页的页码号，通过 first 来指示
        if left[0] > 1:
            first = True
    else:
        # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
        # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
        left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
        right = page_range[page_number:page_number + 2]

        # 是否需要显示最后一页和最后一页前的省略号
        if right[-1] < total_pages - 1:
            right_has_more = True
        if right[-1] < total_pages:
            last = True

        # 是否需要显示第 1 页和第 1 页后的省略号
        if left[0] > 2:
            left_has_more = True
        if left[0] > 1:
            first = True

    data = {
        'left': left,
        'right': right,
        'left_has_more': left_has_more,
        'right_has_more': right_has_more,
        'first': first,
        'last': last,
    }
    return data


def archives(request, year, month):
    entries = models.Entry.objects.filter(created_time__year=year, created_time__month=month)
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    # 获取分页对象
    page_date = pagination_data(paginator, page)

    return render(request, 'blog/index.html', locals())


# 专门处理403作错误页面的视图函数
def permission_denied(request):

    return render(request, 'blog/403.html', locals())


# 处理资源不存在的视图函数
def page_not_found(request):
    return render(request, 'blog/404.html', locals())


# 处理服务器内部错误
def page_error(request):
    return render(request, 'blog/500.html', locals())


# 微博第三方登录,微博的回调函数会回访我们在前端定义好的url
def login(request):
    import requests

    # 获取微博回调的code
    code = request.GET.get('code', None)
    if code is None:
        # 重定向到网站的首页
        return redirect('/')
    # 如果code不为空,获取token令牌
    access_token_url = "https://api.weibo.com/oauth2/access_token?client_id={}&client_secret={}&" \
                       "grant_type=authorization_code&" \
                       "redirect_uri=http://www.yoursite.com/login&code={}".format(
                            settings.CLIENT_ID, settings.APP_SECRET, code
                        )

    # 我们使用requests模块访问微博登录的url
    value = requests.post(access_token_url)
    # 微博接口会返回一个json格式的数据
    data = value.text

    # 把json格式的数据转换为python格式的字典
    data_dict = json.loads(data)

    # 获取token令牌
    token = data_dict['access_token']
    uid = data_dict['uid']

    # 把登录相关信息保存到session中
    request.session['token'] = token
    request.session['uid'] = uid
    # 设置用户的登录状态为true
    request.session['login'] = True

    # 获取微博登录用户的信息,url是微博的api提供的
    user_info_url = 'https://api.weibo.com/2/users/show.json?access_token={}&uid={}'.format(token, uid)
    user_info = requests.get(user_info_url)
    # json格式的数据转换为python字典格式的数据
    user_info_dict = json.loads(user_info.text)

    # 获取微博登录用户的用户名和头像的url
    request.session['screen_name'] = user_info_dict['screen_name']
    request.session['profile_image_url'] = user_info_dict['profile_image_url']

    # 如果没有提供next的话,就使用 '/'来访问
    return redirect(request.GET.get('next', '/'))


# 用户登出
def logout(request):

    # 如果用户登录状态下点击登出,就清除所有session中的数据
    if request.session['login']:

        del request.session['login']
        del request.session['uid']
        del request.session['token']
        del request.session['screen_name']
        del request.session['profile_image_url']

        return redirect(request.Get.get('next', '/'))
    else:
        return redirect('/')


# 评论回复的视图
# 从前端获取评论的id
def reply(request, comment_id):

    # 如果用户不是管理员或者微博登录用户的话
    if not request.session.get('login', None) and not request.user.is_authenticated():
        return redirect('/')

    # 获取父评论的id
    parent_comment = get_object_or_404(comment_models.Comment, id=comment_id)
    return render(request, 'blog/reply.html', locals())
