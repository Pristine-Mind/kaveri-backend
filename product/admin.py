from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Product,
    ProductCategory,
    CartItem,
    Cart,
    Review,
    ReviewPhoto,
    Shipping,
    Order,
    OrderTracking,
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display: tuple[str, str, str] = ("name", "description", "image_preview")
    search_fields: tuple[str] = ("name",)
    readonly_fields: tuple[str] = ("image_preview",)

    def image_preview(self, obj: ProductCategory) -> str:
        """
        Show an image preview in the admin if an image is available.
        """
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.image.url)
        return "No image available"

    image_preview.short_description = "Image Preview"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display: tuple[str, str, str, str, str] = ("name", "category", "price", "stock_status", "featured")
    list_filter: tuple[str] = ("category", "stock_status", "featured")
    search_fields: tuple[str] = ("name", "description")
    ordering: tuple[str] = ("name",)
    readonly_fields: tuple[str] = ("image_preview",)

    fieldsets: tuple = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "price",
                    "category",
                    "stock_status",
                    "image",
                    "image_preview",
                    "featured",
                    "stock",
                )
            },
        ),
    )

    def image_preview(self, obj: Product) -> str:
        """
        Show an image preview in the admin if an image is available.
        """
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.image.url)
        return "No image available"

    image_preview.short_description = "Image Preview"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ("product", "quantity", "get_total_price")
    readonly_fields = ("get_total_price",)

    def get_total_price(self, obj):
        return obj.get_total_price()

    get_total_price.short_description = "Total Price"


class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "session_key", "created_at", "get_total_price")
    list_filter = ("created_at", "user")
    search_fields = ("session_key", "user__username")
    inlines = [CartItemInline]
    readonly_fields = ("created_at",)

    def get_total_price(self, obj):
        return obj.get_total_price()

    get_total_price.short_description = "Total Price"


class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "get_total_price")
    list_filter = ("cart", "product")
    search_fields = ("product__name", "cart__session_key", "cart__user__username")
    readonly_fields = ("get_total_price",)

    def get_total_price(self, obj):
        return obj.get_total_price()

    get_total_price.short_description = "Total Price"


class ReviewPhotoInline(admin.TabularInline):
    model = Review.photos.through
    extra = 1
    verbose_name = "Review Photo"
    verbose_name_plural = "Review Photos"


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "rating", "created_at", "updated_at")
    list_filter = ("rating", "created_at")
    search_fields = ("name", "email", "review_text", "product__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ReviewPhotoInline]


class ReviewPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "uploaded_at")
    search_fields = ("id",)
    readonly_fields = ("uploaded_at",)


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "first_name", "last_name", "city", "state", "created_at")
    search_fields = ("first_name", "last_name", "email", "city", "state")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "total_price", "delivery_charge", "order_status", "created_at")
    list_filter = ("order_status",)
    search_fields = ("cart__id", "shipping__first_name", "shipping__last_name")

    def save_model(self, request, obj, form, change):
        if 'order_status' in form.changed_data:
            # Add tracking record for the status change
            OrderTracking.objects.create(
                order=obj,
                status=obj.order_status,
                updated_by=request.user.username
            )
        super().save_model(request, obj, form, change)


admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewPhoto, ReviewPhotoAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
