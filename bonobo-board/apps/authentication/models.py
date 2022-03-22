# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# import unicodedata

# from django.apps import apps
from django.db import models
# from django.utils.crypto import salted_hmac
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

# class BonoboUserManager(models.Manager):

#     def _create_user(self, email, **extra_fields):
#         if not email:
#             raise ValueError("The given email must be set")
#         email = self.normalize_email(email)
#         GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
#         user = self.model(email=email, **extra_fields)
#         user.save(using=self._db)
#         return user

#     def create_user(self, email, **extra_fields):
#         return self._create_user(email, **extra_fields)


#     @classmethod
#     def normalize_email(cls, email):
#         email = email or ''
#         try:
#             email_name, domain_part = email.strip().rsplit('@', 1)
#         except ValueError:
#             pass
#         else:
#             email = email_name + '@' + domain_part.lower()
#         return email

#     def get_by_natural_key(self, username):
#         return self.get(**{self.model.USERNAME_FIELD: username})

# class BonoboUser(models.Model):
#     email = models.EmailField(
#         _('email_address'),
#         max_length=254,
#         unique=True,
#         help_text=_('Required. 254 characters or fewer.'),
#         error_messages={
#             'unique': _('A user with that email already exists.')
#         }
#     )
#     is_active = models.BooleanField(
#         _('active'),
#         default=True,
#         help_text=_(
#             'Designates whether this user should be treated as active. '
#             'Unselect this instead of deleting accounts.'
#         )
#     )

#     objects = BonoboUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     class Meta:
#         verbose_name = _('user')
#         verbose_name_plural = _('users')
#         swappable = 'AUTH_USER_MODEL'

#     def __str__(self):
#         return self.get_username()

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
    
#     def get_username(self):
#         return getattr(self, self.USERNAME_FIELD)

#     def clean(self):
#         setattr(self, self.USERNAME_FIELD, self.normalize_username(self.get_username()))
#         self.email = self.__class__.objects.normalize_email(self.email)

#     def natural_key(self):
#         return (self.get_username(),)

#     @property
#     def is_anonymous(self):
#         return False

#     @property
#     def is_authenticated(self):
#         return True

#     def get_session_auth_hash(self):
#         key_salt = "apps.authentication.models.BonoboUser.get_session_auth_hash"
#         return salted_hmac(
#             key_salt,
#             self.email,
#             algorithm='sha256',
#         ).hexdigest()

#     @classmethod
#     def get_email_field_name(cls):
#         try:
#             return cls.EMAIL_FIELD
#         except AttributeError:
#             return 'email'

#     @classmethod
#     def normalize_username(cls, username):
#         return unicodedata.normalize('NFKC', username) if isinstance(username, str) else username

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
    dualis_scraped_data = models.CharField(
        verbose_name='dualis scraped data',
        max_length=255,
        unique=False,
        default=""
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
