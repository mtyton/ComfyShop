from typing import Any

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import QuerySet


def send_mail(to: list[str], docs: Any, order_number: str, subject: str, body: str):
    message = EmailMessage(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=to)
    for doc in docs:
        message.attach(f"{order_number}.pdf", doc, "application/pdf")
    return bool(message.send())


def notify_user_about_order(customer_email, docs, order_number):
    return send_mail(
        to=[customer_email],
        docs=docs,
        order_number=order_number,
        subject=f"Zamówienie {order_number}",
        body="Dokumenty dla Twojego zamówienia",
    )


def notify_manufacturer_about_order(manufacturer_email, docs, order_number):
    return send_mail(
        to=[manufacturer_email],
        docs=docs,
        order_number=order_number,
        subject=f"Złożono zamówienie {order_number}",
        body="Dokumenty dla złożonego zamówienia",
    )
