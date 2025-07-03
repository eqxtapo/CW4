from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from config.settings import CACHE_ENABLED, EMAIL_HOST_USER
from mailing.models import AttemptMailing, Mailing

from .forms import EmailForm


def run_mail(request, pk):
    """Функция запуска рассылки по требованию"""
    mailing = get_object_or_404(Mailing, id=pk)
    for recipient in mailing.client.all():
        if mailing.is_active is True:
            try:
                mailing.status = Mailing.LAUNCHED
                mailing.first_sending = timezone.now()
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.content,
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[recipient.mail],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Ошибка при отправке письма для {recipient.mail}: {str(e)}")
                AttemptMailing.objects.create(
                    date_attempt=timezone.now(),
                    status=Mailing.FINISHED,
                    server_response=str(e),
                    mailing=mailing,
                )
        else:
            print(f"Рассылка заблокирована!")
    if mailing.end_sending and mailing.end_sending <= timezone.now():

        mailing.status = Mailing.FINISHED
    mailing.save()
    return redirect("mailing:mailing_list")


def get_mailing_from_cache():
    """Получение данных по рассылкам из кэша, если кэш пуст берем из БД."""

    if not CACHE_ENABLED:
        return Mailing.objects.all()
    key = "mailing_list"
    cache_mail = cache.get(key)
    if cache_mail is not None:
        return cache_mail
    cache_mail = Mailing.objects.all()
    cache.set(cache_mail, key)
    return cache_mail


def get_attempt_from_cache():
    """Получение данных по попыткам  из кэша, если кэш пуст берем из БД."""

    if not CACHE_ENABLED:
        return AttemptMailing.objects.all()
    key = "attempt_list"
    cache_attempt = cache.get(key)
    if cache_attempt is not None:
        return cache_attempt
    cache_mail = Mailing.objects.all()
    cache.set(cache_attempt, key)
    return cache_attempt


@login_required
def block_mailing(request, pk):
    mailing = Mailing.objects.get(pk=pk)
    mailing.is_active = {mailing.is_active: False, not mailing.is_active: True}[True]
    mailing.end_sending = timezone.now()
    mailing.save()
    return redirect(reverse("mailing:mailing_list"))
