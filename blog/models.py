from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# 博客的分类模型
class Category(models.Model):

    name = models.CharField(max_length=128, verbose_name="博客分类")

    # 打印对象的时候,返回的信息
    def __str__(self):
        return self.name

    # 元类
    class Meta:
        verbose_name = "博客分类"
        # 复数形式展示(英文存在这个问题,中文并不存在)
        verbose_name_plural = "博客分类"


# 博客的标签模型
class Tag(models.Model):

    name = models.CharField(max_length=128, verbose_name="博客标签")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "博客标签"
        verbose_name_plural = "博客标签"


# 博客的文章模型
class Entry(models.Model):
    title = models.CharField(max_length=128, verbose_name="文章标题")
    # 博客的作者,使用安全框架自带的User对象模型,一对多的关系,一篇文章只能有一个作者,外键的方式
    author = models.ForeignKey(User, verbose_name="博客作者")
    # 允许博客不配图
    # null=True 允许保存到数据库的此字段的内容为空
    # blank=True 允许后台的admin展示的时候,此字段为空
    # 最好把null的取值和blank的取值保持一致
    # blog_images: 把图片上传到该文件夹之下,需要在配置文件中进行文件配置
    img = models.ImageField(upload_to="blog_images", null=True, blank=True, verbose_name="博客配图")
    # 博客正文
    body = models.TextField(verbose_name="博客正文")
    # 博客的摘要,允许博客的摘要为true
    abstract = models.TextField(max_length=256, blank=True, null=True, verbose_name="博客摘要")
    # 博客的访问量,不能为负数,也不能为浮点数,只能为正整数,初始值都为0
    visiting = models.PositiveIntegerField(default=0, verbose_name="博客访问量")
    # 博客的分类,分类和博客是多对多的关系
    category = models.ManyToManyField("Category", verbose_name="博客分类")
    # 博客的标签,标签和博客是多对多关系
    tags = models.ManyToManyField("Tag", verbose_name="博客标签")
    # 博客创建时间,会自动把创建的时间添加
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="博客创建时间")
    # 博客修改时间,会自动把修改时间添加
    modified_time = models.DateTimeField(auto_now=True, verbose_name="博客修改时间")

    def __str__(self):
        return self.title

    # 给我们每一篇文章生成专属的链接
    def get_absolute_url(self):

        # 参数一: app名称(app_name):url名称(name='blog_detail')
        # 会把文章的url解析成下列格式: http://127.0.0.1/blog/3
        # 进行url的反解析,根据url的名称把url的路径返回给前端 blog_id名称和前端变量名称保持一致
        return reverse('blog:blog_detail', kwargs={'blog_id': self.id})

    # 点击一篇博文,增加文章的浏览量
    def increase_visiting(self):
        # 给文章的访问量 + 1
        self.visiting += 1
        # 当访问这个方法的时候,只增加visiting的数据,其他字段的数据不保存更新
        self.save(update_fields=['visiting'])

    class Meta:
        # 添加排序, - 代表倒序排列
        # !!! 一定要给进行查询的对象添加排序依据,否则之后的操作可能会报错
        ordering = ["-created_time"]
        verbose_name = "博客内容"
        verbose_name_plural = "博客内容"



