"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from .widgets import MultiEmailWidget

#src: https://github.com/fle/django-multi-email-field/blob/7dcc5f4e0aee1c935abdbb94aa4edff8521938d7/multi_email_field/forms.py
class MultiEmailField(forms.Field):
    message = 'Enter valid email addresses.'
    code = 'invalid'
    widget = MultiEmailWidget

    def to_python(self, value):
        "Normalize data to a list of strings."
        # Return None if no input was given.
        if not value:
            return []
        return [v.strip() for v in re.split(';|,', value) if v != ""]

    def validate(self, value):
        """ Check if value consists only of valid emails. """

        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)
        try:
            for email in value:
                validate_email(email)
        except ValidationError:
            raise ValidationError(self.message, code=self.code)


class ContactForm(forms.Form):
    empfänger = MultiEmailField(
         widget=forms.TextInput(
            attrs={
                "placeholder": "Empfänger",
                "class": "form-control",
                'autocomplete': 'off'
            }
        ),required=True)
    cc = MultiEmailField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Cc",
                "class": "form-control",
                'autocomplete': 'off'
            }
        ),
        required=False)
    bcc = MultiEmailField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Bcc",
                "class": "form-control",
                'autocomplete': 'off'
            }
        ),
        required=False)
    betreff = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Betreff",
                "class": "form-control"
            }
        ),
        required=True)
    nachricht = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Nachricht. Bitte sei immer freundlich!",
                "class": "form-control"
            }
        ),
        required=True)
