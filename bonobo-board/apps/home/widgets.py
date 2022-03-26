"""
Widgets.py
"""

from django.forms.widgets import Textarea
from django.core.exceptions import ValidationError
from django.core import validators

# src:
# https://github.com/fle/django-multi-email-field/blob/7dcc5f4e0aee1c935abdbb94aa4edff8521938d7/multi_email_field/widgets.py

MULTI_EMAIL_FIELD_EMPTY_VALUES = validators.EMPTY_VALUES + ('[]', )

try:
    from django.utils import six

    string_types = six.string_types
except ImportError:
    string_types = str


class MultiEmailWidget(Textarea):
    is_hidden = False

    def prep_value(self, value):
        """ Prepare value before effectively render widget """
        if value in MULTI_EMAIL_FIELD_EMPTY_VALUES:
            return ""
        elif isinstance(value, string_types):
            return value
        elif isinstance(value, list):
            return "\n".join(value)
        raise ValidationError('Invalid format.')

    def render(self, name, value, **kwargs):
        value = self.prep_value(value)
        return super(MultiEmailWidget, self).render(name, value, **kwargs)