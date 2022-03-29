# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# import unicodedata

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class BonoboUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class BonoboUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    dualis_scraped_data = models.BinaryField(
        verbose_name='dualis scraped data',
        # max_length=255,
        unique=False
    )
    zimbra_token = models.CharField(
        verbose_name='zimbra auth token',
        max_length=255,
        unique=False,
        default=""
    )
    zimbra_accountname = models.CharField(
        verbose_name='zimbra account name',
        max_length=255,
        unique=False,
        default=""
    )
    zimbra_name = models.CharField(
        verbose_name='zimbra real name',
        max_length=255,
        unique=False,
        default=""
    )
    zimbra_contacts = models.CharField(
        verbose_name='zimbra contact list',
        max_length=255,
        unique=False,
        default=""
    )
    zimbra_headers = models.CharField(
        verbose_name='zimbra headers',
        max_length=255,
        unique=False,
        default=""
    )
    moodle_token = models.CharField(
        verbose_name='moodle token',
        max_length=255,
        unique=False,
        default=""
    )
    moodle_scraped_data = models.CharField(
        verbose_name='moodle scraped data',
        max_length=255,
        unique=False,
        default=""
    )
    lectures = models.CharField(
        verbose_name='scraped lectures',
        max_length=255,
        unique=False,
        default=""
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = BonoboUserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    user_objects = {
        "dualis": None,
        "lecture": None,
        "moodle": None,
        "zimbra": None
    }

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
