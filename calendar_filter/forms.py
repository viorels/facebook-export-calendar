from django import forms
from django.forms.widgets import TextInput, CheckboxInput


EVENT_STATUS_CHOICES = (('accepted', 'Accepted'),
                        ('tentative', 'Tentative'),
                      ('needs-action', 'Needs Action'))

class CalendarForm(forms.Form):
    url = forms.URLField()
    status = forms.MultipleChoiceField(choices=EVENT_STATUS_CHOICES)