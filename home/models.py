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


# models.py
from django.db import models

from wagtail.images.models import Image, AbstractImage, AbstractRendition


class CustomImage(AbstractImage):
    # Add any extra fields to image here

    # eg. To add a caption field:
    caption = models.CharField(max_length=255, blank=True, verbose_name="Автор")
    origin = models.CharField(max_length=255, blank=True, verbose_name="Сылка на оригинал")

    admin_form_fields = Image.admin_form_fields + (
        # Then add the field names here to make them appear in the form:
        'caption', 'origin'
    )


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )
