from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(verbose_name=_("Email Address"), unique=True)
    username = models.CharField(
        verbose_name=_("Username"),
        max_length=150,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
    )
    full_name = models.CharField(
        verbose_name=_("Full Name"), max_length=512, null=True, blank=True, help_text=_("Full name is auto generated.")
    )
    is_verified = models.BooleanField(verbose_name=_("Is Verified"), default=False)
    groups = models.ManyToManyField(Group, related_name="raffae_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="raffae_user_permissions", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_full_name(self):
        return " ".join([name for name in [self.first_name, self.last_name] if name]) or self.email

    def save(self, *args, **kwargs):
        is_new_verified = self.is_verified and self.pk
        print(is_new_verified, "nneww")

        if not self.pk:
            self.full_name = self.get_full_name()
        super().save(*args, **kwargs)
        # Send email when is_verified is set to True
        if is_new_verified:
            self.send_verification_email()

    def send_verification_email(self):

        subject = "Your Account Has Been Verified"

        # HTML email content
        message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Account Verified</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
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
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://scontent.fktm8-1.fna.fbcdn.net/v/t39.30808-6/458943246_8181302661977641_4224396525692647175_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=86c6b0&_nc_ohc=rcLWB5Chs4AQ7kNvgEvAi3O&_nc_oc=Adhe4ufQOjdD7pZ0a4FL46WvFrrlvjqEe1FHMtLRS3N7jgyja61k3iP8LsYTQrqDa2U7_K7ahCqT2CfqdawJoxee&_nc_zt=23&_nc_ht=scontent.fktm8-1.fna&_nc_gid=AQ-5THGzniMsI7JlFv5Bng_&oh=00_AYAloihmpiJ2C-YPT5w2YJdtrcGi1iFMEkrdOLwO-SfBdA&oe=677D7D9B" alt="Kaveri International Logo" />
                </div>
                <div class="content">
                    <h2>Congratulations, {self.get_full_name()}!</h2>
                    <p>We're excited to let you know that your account has been successfully verified.</p>
                    <p>If you have any questions, feel free to reply to this email or contact our support team at <a href="mailto:info@kaverintl.com">info@kaverintl.com</a>.</p>
                    <p>We will notify you of any further updates regarding your account.</p>
                    <p>Best regards,<br>Kaveri InternationalTeam</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Kaveri International. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        if self.is_verified:
            print(f"Sending email from {settings.SECONDARY_FROM_EMAIL}")  # Debugging print
            from_email = settings.SECONDARY_FROM_EMAIL  # Use info@kaveriintl.com for verification emails

        print(f"From email: {from_email}")  # Debugging print
        recipient_list = [self.email]

        # Send email with HTML content
        send_mail(
            subject,
            "Your account has been successfully verified.",
            from_email,
            recipient_list,
            html_message=message,  # HTML message
        )


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="User"
    )
    business_name = models.CharField(
        max_length=255,
        verbose_name="Business Name"
    )
    business_address = models.TextField(
        verbose_name="Business Address"
    )
    business_city = models.CharField(
        max_length=255,
        verbose_name="City"
    )
    business_state = models.CharField(
        max_length=2,
        verbose_name="State (US)",
        help_text="Use standard 2-letter state code, e.g. CA, NY, TX, etc."
    )
    business_zip = models.CharField(
        max_length=20,
        verbose_name="ZIP Code"
    )
    business_phone = models.CharField(
        max_length=50,
        verbose_name="Business Phone"
    )
    license_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name or f"Profile of {self.user.email}"


class Recovery(models.Model):
    """Password recovery"""

    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    token = models.CharField(verbose_name=_("token"), max_length=32, editable=False)

    class Meta:
        verbose_name = _("Recovery")
        verbose_name_plural = _("Recoveries")

    def __str__(self):
        return self.user.username


class BeerClubMember(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
