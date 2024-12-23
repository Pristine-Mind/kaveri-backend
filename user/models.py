from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    groups = models.ManyToManyField(Group, related_name="raffae_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="raffae_user_permissions", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_full_name(self):
        return " ".join([name for name in [self.first_name, self.last_name] if name]) or self.email

    def save(self, *args, **kwargs):
        self.full_name = self.get_full_name()
        return super().save(*args, **kwargs)


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
    phone = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
