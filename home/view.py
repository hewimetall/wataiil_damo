import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

from wagtail.core.models import Page

from .models import Annotate

class AnnotateView(View):
    http_method_names = ['put', 'get']

    def get(self,  *args, **kwargs):
        page_id = kwargs['page_id']
        obj_list = [ i.json_data for i in Annotate.manager.filter(page__id=page_id)]
        return JsonResponse(list(obj_list), safe=False)


    def create_new(self, json_date, page,id_messege):
        del json_date['event']
        try:
            obj: Annotate = Annotate.manager.get(id_messege=id_messege,page =page)
            obj.id_messege = json_date['id']
            obj.json_data = json_date
            obj.save()
        except Annotate.DoesNotExist:
            obj = Annotate(
                id_messege=json_date['id'],
                json_data=json_date,
                page=page,
                submitter=self.request.user
            )
            obj.save()

    def put(self, *args, **kwargs):
        page_id = kwargs['page_id']
        page: Page = get_object_or_404(Page, id=page_id)
        json_data:dict = json.loads(self.request.body)
        if json_data['event'] == 'createAnnotation':
            self.create_new(json_data, page, json_data['id'])
        else:
            previous = json_data.pop('previous')
            self.create_new(json_data, page, previous['id'])
        return HttpResponse("200")
