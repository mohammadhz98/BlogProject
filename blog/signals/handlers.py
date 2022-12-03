from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .. import models



@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        token = Token.objects.create(user=instance)


@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_member_for_user(sender, instance=None, created=False, **kwargs):
    if created:
        models.Member.objects.create(user=instance)


@receiver(post_save,sender=models.Comment)
def create_member_for_user(sender, instance=None, created=False, **kwargs):
    if created:
        if not get_user_model().objects.filter(email=instance.email).exists():
            models.Guest.objects.get_or_create(email=instance.email)



