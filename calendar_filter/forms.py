from django import forms
from django.forms.widgets import TextInput, CheckboxInput


EVENT_STATUS_CHOICES = (('accepted', 'Accepted'),
                        ('tentative', 'Tentative'),
                      ('needs-action', 'Needs Action'))

class CalendarForm(forms.Form):
    url = forms.CharField(
        label="Facebook events link",
        widget=TextInput(attrs={
            "size": "40",
            "placeholder": "webcal://www.facebook.com/ical/u.php?uid=..."})
        )
    status = forms.MultipleChoiceField(
        choices=EVENT_STATUS_CHOICES,
        required=True,
        label="Allowed statuses")