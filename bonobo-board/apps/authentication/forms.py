# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms


class LoginForm(forms.Form):
    username = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "sXXXXXX@student.dhbw-mannheim.de",
                "class": "form-control"
            }
        ), required=True)
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Passwort",
                "class": "form-control"
            }
        ), required=True)
    course = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Kurs Name",
                "class": "form-control"
            }
        ), required=True)
