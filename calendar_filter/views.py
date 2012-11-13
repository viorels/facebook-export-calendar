from django.views.generic.base import TemplateView, View
from django.http import HttpResponse
from django.conf import settings

import requests
import vobject

from forms import CalendarForm


class HomeView(TemplateView):
    template_name = 'home.html'


class CalendarResponseMixin(object):
    """
    A mixin that can be used to render a Webcal response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        charset = 'utf-8'
        response = self.convert_context_to_vobject(context)
        response_kwargs['content_type'] = 'text/calendar;charset=%s' % charset
        # TODO: Content-Length
        # response_kwargs['content_length'] = len(response)
        return self.response_class(
            response,
            **response_kwargs
        )

    def convert_context_to_vobject(self, context):
        return context['calendar'].serialize()

class FilterView(CalendarResponseMixin, View):
    def get(self, request, *args, **kwargs):
        context = {'calendar': self.filter_calendar()}
        return self.render_to_response(context)

    def get_calendar(self):
        uid = self.request.GET.get('uid')
        key = self.request.GET.get('key')
        if uid and key:
            url = settings.FACEBOOK_CALENDAR_URL
            # TODO: timeout
            response = requests.get(url, params={'uid': uid, 'key': key})
        else:
            raise ValueError("Required parameters uid and key")
        return vobject.readOne(response.text)

    def filter_calendar(self):
        allowed_status = set(self.request.GET.getlist('status', []))
        calendar = self.get_calendar()
        events = [e for e in calendar.vevent_list
                  if e.partstat.value.lower() in allowed_status]
        calendar.vevent_list = events
        return calendar