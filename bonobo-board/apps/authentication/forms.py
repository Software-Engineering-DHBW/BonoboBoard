# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "sXXXXXX@student.dhbw-mannheim.de",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Passwort",
                "class": "form-control"
            }
        ))
    course = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Kurs Name",
                "class": "form-control"
            }
        ))
