from django.utils.html import format_html
from django.templatetags.static import static
from wagtail.core import hooks


class UserbarPuppyLinkItem:
    def render(self, request):
        return """
        <div class="wagtail-userbar__item ">
    <div class="wagtail-action">
        <a id="wagtail-toggle-mode" >
         Переключить  режим анотации
        </a>
    </div>
</div>"""

@hooks.register('construct_wagtail_userbar')
def add_puppy_link_item(request, items):
    return items.append( UserbarPuppyLinkItem() )


@hooks.register('insert_editor_css')
def get_data():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static('css/test_static.css')
    )
