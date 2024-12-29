from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    if created:
        subject = f"Order Confirmation - Order #{instance.id}"

        # Compose plain text message
        plain_message = (
            f"Dear {instance.cart.user.first_name},\n\n"
            f"Thank you for your order! Your order #{instance.id} has been successfully placed.\n\n"
            f"Order Details:\n"
            f"Total Price: ${instance.total_price}\n"
            f"Delivery Charge: ${instance.delivery_charge}\n"
            f"Order Status: {instance.order_status}\n\n"
            f"We will notify you once your order is shipped.\n\n"
            f"Best regards,\n"
            f"BrewShop Team"
        )

        # Compose HTML message
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Order Confirmation</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 5px;
                    max-width: 600px;
                    margin: auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                }}
                .content {{
                    line-height: 1.6;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    font-size: 12px;
                    color: #777777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Thank You for Your Order!</h2>
                </div>
                <div class="content">
                    <p>Dear {instance.cart.user.first_name},</p>
                    <p>Thank you for your order! Your order <strong>#{instance.id}</strong> has been successfully placed.</p>
                    <h3>Order Details:</h3>
                    <ul>
                        <li><strong>Total Price:</strong> ${instance.total_price}</li>
                        <li><strong>Delivery Charge:</strong> ${instance.delivery_charge}</li>
                        <li><strong>Order Status:</strong> {instance.order_status}</li>
                    </ul>
                    <p>We will notify you once your order is shipped.</p>
                    <p>Best regards,<br>Kaveri International Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Kaveri International. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        recipient_list = [instance.shipping.email]

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
            html_message=html_message,
        )
