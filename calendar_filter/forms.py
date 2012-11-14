from django import forms
from django.forms.widgets import TextInput, CheckboxInput


EVENT_STATUS_CHOICES = (('accepted', 'Accepted'),
                        ('tentative', 'Tentative'),
                      ('needs-action', 'Needs Action'))

class CalendarForm(forms.Form):
    url = forms.CharField(label="Facebook events link")
    status = forms.MultipleChoiceField(
        choices=EVENT_STATUS_CHOICES,
        required=True,
        label="Accepted statuses")