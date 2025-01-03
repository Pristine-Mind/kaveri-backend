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
                /* Import Google Fonts */
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

                body {{
                    font-family: 'Roboto', Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                    margin: 0;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 10px;
                    max-width: 600px;
                    margin: auto;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e0e0e0;
                }}
                .header img {{
                    max-width: 150px;
                    height: auto;
                }}
                .content {{
                    padding: 20px 0;
                    line-height: 1.6;
                    color: #333333;
                }}
                .content h3 {{
                    color: #d35400;
                    margin-bottom: 10px;
                }}
                .order-details {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .order-details th, .order-details td {{
                    text-align: left;
                    padding: 12px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .order-details th {{
                    background-color: #f8f8f8;
                    color: #555555;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 25px;
                    margin-top: 20px;
                    background-color: #d35400;
                    color: #ffffff !important;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                .button:hover {{
                    background-color: #c0392b;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    font-size: 12px;
                    color: #777777;
                    border-top: 2px solid #e0e0e0;
                }}
                .social-icons {{
                    margin-top: 10px;
                }}
                .social-icons a {{
                    margin: 0 5px;
                    display: inline-block;
                }}
                .social-icons img {{
                    width: 24px;
                    height: 24px;
                }}
                @media only screen and (max-width: 600px) {{
                    .container {{
                        padding: 20px;
                    }}
                    .header img {{
                        max-width: 120px;
                    }}
                    .button {{
                        width: 100%;
                        text-align: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://scontent.fktm8-1.fna.fbcdn.net/v/t39.30808-6/458943246_8181302661977641_4224396525692647175_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=86c6b0&_nc_ohc=rcLWB5Chs4AQ7kNvgEvAi3O&_nc_oc=Adhe4ufQOjdD7pZ0a4FL46WvFrrlvjqEe1FHMtLRS3N7jgyja61k3iP8LsYTQrqDa2U7_K7ahCqT2CfqdawJoxee&_nc_zt=23&_nc_ht=scontent.fktm8-1.fna&_nc_gid=AQ-5THGzniMsI7JlFv5Bng_&oh=00_AYAloihmpiJ2C-YPT5w2YJdtrcGi1iFMEkrdOLwO-SfBdA&oe=677D7D9B" alt="Kaveri International Logo" />
                </div>
                <div class="content">
                    <h2>Thank You for Your Order, {instance.cart.user.first_name}!</h2>
                    <p>We're excited to let you know that your order <strong>#{instance.id}</strong> has been successfully placed.</p>
                    <h3>Order Details:</h3>
                    <table class="order-details">
                        <tr>
                            <th>Item</th>
                            <th>Price</th>
                        </tr>
                        {''.join([f"<tr><td>{item.product.name} (x{item.quantity})</td><td>${item.product.price * item.quantity}</td></tr>" for item in instance.cart.cartitem_set.all()])}
                        <tr>
                            <td><strong>Total Price:</strong></td>
                            <td><strong>${instance.total_price}</strong></td>
                        </tr>
                        <tr>
                            <td><strong>Delivery Charge:</strong></td>
                            <td><strong>${instance.delivery_charge}</strong></td>
                        </tr>
                        <tr>
                            <td><strong>Order Status:</strong></td>
                            <td><strong>{instance.order_status}</strong></td>
                        </tr>
                    </table>
                    <p>If you have any questions, feel free to reply to this email or contact our support team.</p>
                    <p>We will notify you once your order is shipped.</p>
                    <p>Best regards,<br>Kaveri International Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Kaveri International. All rights reserved.</p>
                    <div class="social-icons">
                        <!-- Replace with your social media links and icons -->
                        <a href="https://www.facebook.com/people/Kaveri-International/61565650737421/"><img src="https://icons8.com/icon/118497/facebook" alt="Facebook" /></a>
                        <a href="https://www.instagram.com/kaveri.international/?fbclid=IwY2xjawFhIT1leHRuA2FlbQIxMAABHWJ9Dfc4PiaGgcIKGkXPv5fcSWJPzpMFuLB2rlFloCiVRitJ7ATq5h-S3Q_aem_RRKJZHfxFCwVp8u7QYSs7A"><img src="https://icons8.com/icon/Xy10Jcu1L2Su/instagram" alt="Instagram" /></a>
                    </div>
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
