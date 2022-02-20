"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms


class LoginForm(forms.Form):
  
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))

    password = forms.CharField(
       widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)