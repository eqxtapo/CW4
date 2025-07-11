from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from mailing.models import AttemptMailing, Mailing


class Command(BaseCommand):
    help = "Отправка рассылки"

    def handle(self, *args, **kwargs):
        mailings = Mailing.objects.filter(
            status__in=[Mailing.CREATED, Mailing.LAUNCHED]
        )
        for mailing in mailings:
            for recipient in mailing.client.all():
                try:
                    send_mail(
                        mailing.message.subject,
                        mailing.message.content,
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    AttemptMailing.objects.create(
                        date_attempt=timezone.now(),
                        status=AttemptMailing.STATUS_OK,
                        response="Email отправлен",
                        mailing=mailing,
                    )

                    print(
                        f"Сообщение {mailing.message.subject} успешно отправлено получателю: {recipient.email}"
                    )
                except Exception as e:
                    AttemptMailing.objects.create(
                        date_attempt=timezone.now(),
                        status=AttemptMailing.STATUS_NOK,
                        response=str(e),
                        mailing=mailing,
                    )
                    print(str(e))
            mailing.save()
