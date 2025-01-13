from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_order_status_email(order):
    """
    Sends an email notification to the customer when the order status changes.
    """
    subject = f"Order #{order.id} Status Update"
    recipient_email = order.shipping.email
    context = {
        'order': order,
        'status': order.order_status,
    }

    html_message = render_to_string('order_status_email.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        html_message=html_message,
    )


def send_payment_success_email(payment):
    """
    Sends an email notification to the customer when the payment is completed.
    """
    subject = f"Payment for Order #{payment.order.id} Successful"
    recipient_email = payment.order.shipping.email
    context = {
        'order': payment.order,
        'amount': payment.amount,
        'payment_method': payment.payment_method,
    }

    html_message = render_to_string('payment_success_email.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        html_message=html_message,
    )
