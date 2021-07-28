from __future__ import absolute_import, unicode_literals

from django.conf.urls import re_path
from .view import Annotate

app_name = 'wagtail_review'

urlpatterns = [
    re_path(r'^api/annotations/<int:page_id>$', Annotate.as_view(), name='annotations'),
]
