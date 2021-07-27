from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views import defaults as default_views

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.contrib.sitemaps.views import sitemap
import blog.views
# from wagtail_review import urls as wagtailreview_urls
from wagtailsharing import urls as wagtailsharing_urls

from home.view import AnnotateView

urlpatterns = [
    path('api/annotations/<int:page_id>', AnnotateView.as_view(), name='annotations'),

    path('django-admin/', admin.site.urls),
    # path('review/', include(wagtailreview_urls)),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('sitemap.xml', sitemap),
    path('robots.txt', blog.views.RobotsView.as_view()),

    path('comments/', include('ab_comment.urls')),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import debug_toolbar

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        path('404/', default_views.page_not_found, kwargs={'exception': Exception("Page not Found")}),
        path('500/', default_views.server_error),
        path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtailsharing_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
