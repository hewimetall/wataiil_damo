import datetime

from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.formats import date_format
from django.utils.dateformat import DateFormat
from django.http import Http404
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag as TaggitTag
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from django.template.defaultfilters import slugify as django_slugify
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.core.fields import RichTextField, StreamField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.search import index
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtailcaptcha.models import WagtailCaptchaEmailForm
from wagtailmetadata.models import MetadataPageMixin
from .blocks import BodyBlock
from wagtail.admin.edit_handlers import HelpPanel

from wagtail.contrib.table_block.blocks import TableBlock


class BlogPage(RoutablePageMixin, Page):
    description = models.CharField(max_length=255, blank=True,verbose_name='Описание')

    content_panels = Page.content_panels + [FieldPanel("description", classname="full")]

    subpage_types = ['PostPage', 'FormPage']

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # https://docs.djangoproject.com/en/3.1/topics/pagination/#using-paginator-in-a-view-function
        paginator = Paginator(self.posts, 2)
        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.object_list.none()

        context["posts"] = posts
        return context

    def get_posts(self):
        return PostPage.objects.descendant_of(self).live().order_by("-post_date")

    @route(r"^(\d{4})/$")
    @route(r"^(\d{4})/(\d{2})/$")
    @route(r"^(\d{4})/(\d{2})/(\d{2})/$")
    def post_by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.search_type = 'date'
        self.search_term = year
        self.posts = self.get_posts().filter(post_date__year=year)
        if month:
            df = DateFormat(datetime.date(int(year), int(month), 1))
            self.search_term = df.format('F Y')
            self.posts = self.posts.filter(post_date__month=month)
        if day:
            self.search_term = date_format(datetime.date(int(year), int(month), int(day)))
            self.posts = self.posts.filter(post_date__day=day)
        return self.render(request)

    @route(r"^(\d{4})/(\d{2})/(\d{2})/(.+)/$")
    def post_by_date_slug(self, request, year, month, day, slug, *args, **kwargs):
        post_page = self.get_posts().filter(slug=slug).first()
        if not post_page:
            raise Http404
        # here we render another page, so we call the serve method of the page instance
        return post_page.serve(request)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = 'tag'
        self.search_term = tag
        self.posts = self.get_posts().filter(tags__slug=tag)
        return self.render(request)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        self.posts = self.get_posts().filter(categories__blog_category__slug=category)
        return self.render(request)

    @route(r"^search/$")
    def post_search(self, request, *args, **kwargs):
        search_query = request.GET.get("q", None)
        self.posts = self.get_posts()
        if search_query:
            self.search_term = search_query
            self.search_type = 'search'
            self.posts = self.posts.search(search_query)
        return self.render(request)

    @route(r'^$')
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return self.render(request)

    def get_sitemap_urls(self, request=None):
        output = []
        posts = self.get_posts()
        for post in posts:
            post_date = post.post_date
            url = self.get_full_url(request) + self.reverse_subpage(
                'post_by_date_slug',
                args=(
                    post_date.year,
                    '{0:02}'.format(post_date.month),
                    '{0:02}'.format(post_date.day),
                    post.slug,
                )
            )

            output.append({
                'location': url,
                'lastmod': post.last_published_at
            })

        return output

    class Meta:
        verbose_name = "Страница блогов"


class PostPage(MetadataPageMixin, Page):
    list_display = ('header_image', 'tags')
    is_yandex = models.BooleanField(verbose_name='Выводится в Яндекс.новостях', default=True)

    is_recl = models.BooleanField(verbose_name='Рекламная', default=False)
    is_pay = models.BooleanField(verbose_name='Платная', default=False)
    is_close_comment = models.BooleanField(verbose_name='Отключать комменарии автоматически', default=True)
    is_picture = models.BooleanField(verbose_name='Отключить главную картинку', default=False)

    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name='Изображения в заголовке'
    )

    post_date = models.DateTimeField(
        verbose_name="Время создания",help_text='Время отображаемое на сайте', default=datetime.datetime.today
    )

    body = StreamField(BodyBlock(), blank=True, verbose_name='Контент на странице')

    tags = ClusterTaggableManager(through="blog.PostPageTag", blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel("header_image"),
        InlinePanel("categories", label="Категории"),
        FieldPanel("tags",classname='full'),
        StreamFieldPanel("body"),
    ]
    promote_panels = [
        HelpPanel(template='menu/help_static.html'),
        FieldPanel("is_yandex"),
    ]+ MetadataPageMixin.promote_panels
    settings_panels = Page.settings_panels + [
        MultiFieldPanel([
        FieldPanel("post_date"),
        FieldPanel('is_close_comment'),
        FieldPanel('is_recl'),
        FieldPanel('is_pay'),
        FieldPanel('is_picture'),
    ], 'Общие настройки'), ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('body'),
    ]

    @cached_property
    def blog_page(self):
        return self.get_parent().specific

    @cached_property
    def canonical_url(self):
        # we should import here to avoid circular import
        from blog.templatetags.blogapp_tags import post_page_date_slug_url

        blog_page = self.blog_page
        return post_page_date_slug_url(self, blog_page)

    def get_sitemap_urls(self, request=None):
        return []

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Страница постов"

class PostPageBlogCategory(models.Model):
    page = ParentalKey(
        "blog.PostPage", on_delete=models.CASCADE, related_name="categories"
    )
    blog_category = models.ForeignKey(
        "blog.BlogCategory", on_delete=models.CASCADE, related_name="post_pages"
    )

    panels = [
        SnippetChooserPanel("blog_category"),
    ]

    class Meta:
        unique_together = ("page", "blog_category")


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e', 'ю': 'yu',
            'я': 'ya'}




@register_snippet
class Tables(models.Model):
    lable = models.CharField(verbose_name='Метка',help_text='Отображаемая имформация при поиске', max_length=120)
    tables = StreamField([
        ('Table',TableBlock()),
        ])

    panels = [

        FieldPanel('lable',classname="full header"),
        FieldPanel('tables',classname="full"),
    ]

    def __str__(self):
        return self.lable
    class Meta:
        verbose_name = "Таблица"
        verbose_name_plural = "Таблицы"



@register_snippet
class Tag(TaggitTag):
    def slugify(self, tag, i=None):
        slug = django_slugify(''.join(alphabet.get(w, w) for w in tag.lower()))
        if i is not None:
            slug += "_%d" % i
        return slug

    class Meta:
        proxy = True
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

class PostPageTag(TaggedItemBase):
    content_object = ParentalKey("PostPage", related_name="post_tags")

    @classmethod
    def tag_model(cls):
        return Tag



class FormField(AbstractFormField):
    page = ParentalKey("FormPage", related_name="custom_form_fields")


class FormPage(WagtailCaptchaEmailForm):
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        InlinePanel("custom_form_fields", label="Form fields"),
        FieldPanel("thank_you_text", classname="full"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email Notification Config",
        ),
    ]

    def get_form_fields(self):
        return self.custom_form_fields.all()

    class Meta:
        verbose_name = "Страница с формой"
