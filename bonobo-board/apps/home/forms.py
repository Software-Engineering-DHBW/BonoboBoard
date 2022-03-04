"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms


class ContactForm(forms.Form):
    empfänger = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email Empfänger",
                "class": "form-control"
            }
        ),
        required=True)
    cc = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Cc",
                "class": "form-control"
            }
        ))
    bcc = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Bcc",
                "class": "form-control"
            }
        ))
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
