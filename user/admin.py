from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BeerClubMember, ContactMessage, User, Profile


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


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

    list_display = ('email', 'username', 'first_name', 'last_name', 'full_name', 'is_verified', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'full_name')}),
        ('Permissions', {'fields': ('is_verified', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
        ),
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'business_name',
        'business_city',
        'business_state',
        'business_zip',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'business_name',
        'user__email',
        'business_city',
        'business_state'
    )
    list_filter = ('business_state',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(BeerClubMember, BeerClubMemberAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
