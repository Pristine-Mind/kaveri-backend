from django.contrib import admin
from .models import BeerClubMember, ContactMessage


class BeerClubMemberAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "created_at")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


admin.site.register(BeerClubMember, BeerClubMemberAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
