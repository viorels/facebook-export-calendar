import time
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.http import http_date
from urlparse import urlparse, urlunparse, parse_qsl
from urllib import urlencode

import requests
import vobject

from forms import CalendarForm


class HomeView(FormView):
    template_name = 'home.html'
    form_class = CalendarForm

    def form_valid(self, form):
        original_url = form.cleaned_data['url']
        status_list = form.cleaned_data['status']
        new_url = self.get_filtered_url(original_url, status_list)
        messages.add_message(self.request, messages.INFO, new_url)
        return super(HomeView, self).form_valid(form)

    def get_success_url(self):
        return reverse('home') + '#step2'

    def get_filtered_url(self, original_url, status_list):
        http_url = original_url.replace('webcal://', 'http://')
        parsed_url = urlparse(http_url)
        args = parse_qsl(parsed_url.query)
        args.extend([('status', status) for status in status_list])
        filtered_url = urlunparse(('webcal',
                                   self.request.get_host(),
                                   reverse('filter'),
                                   None,
                                   urlencode(args),
                                   None))
        return filtered_url

class CalendarResponseMixin(object):
    """
    A mixin that can be used to render a Webcal response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        charset = 'utf-8'
        response_vobject = self.convert_context_to_vobject(context)
        response_kwargs['content_type'] = 'text/calendar;charset=%s' % charset
        response = self.response_class(
            response_vobject,
            **response_kwargs
        )
        response['Content-Length'] = len(response_vobject)
        return response

    def convert_context_to_vobject(self, context):
        return context['calendar'].serialize()

class FilterView(CalendarResponseMixin, View):
    def get(self, request, *args, **kwargs):
        context = {'calendar': self.filter_calendar()}
        response = self.render_to_response(context)
        response['Expires'] = http_date(time.time() + 60*15)
        return response

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
