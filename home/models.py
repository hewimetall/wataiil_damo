from django.db import models

from wagtail.core.models import Page
from django.db import models
from django.conf import settings
from modelcluster.fields import ParentalKey
from wagtail.core.models import Page

class HomePage(Page):
    pass


class Annotate(models.Model):
    id_messege = models.CharField(max_length=120)
    page = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE, editable=False)
    status = models.CharField(max_length=30, default='open', editable=False)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    json_data = models.JSONField(verbose_name="Коментарий")

    manager  = models.Manager()