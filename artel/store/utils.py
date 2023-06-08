from django.core.mail import EmailMessage
from django.conf import settings


# TODO - add celery task for sending not sent earlier
def send_mail(order_doc):
    order = order_doc.order
    message = EmailMessage(
        subject=f"Zamówienie {order.order_number}",
        body="Dokumenty dla Twojego zamówienia",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.customer.email]
    )
    message.attach(f"{order.order_number}.pdf", order_doc.document, "application/pdf")
    sent = bool(message.send())
    order_doc.sent = sent
    order_doc.save()
    return sent
