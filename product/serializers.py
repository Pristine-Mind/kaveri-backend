from django.utils.translation import gettext

from rest_framework import serializers
from .models import (
    Product,
    ProductCategory,
    Review,
    ReviewPhoto,
    Cart,
    CartItem,
    Shipping,
    Order,
    OrderTracking,
    Payment,
    Store,
)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "description", "image"]


class ProductSerializer(serializers.ModelSerializer):
    category: ProductCategorySerializer = ProductCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "category", "stock_status", "image", "featured"]


class ReviewPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewPhoto
        fields = ["id", "image", "uploaded_at"]


class ReviewSerializer(serializers.ModelSerializer):
    photos = ReviewPhotoSerializer(many=True, required=False, allow_null=True)

    MAX_NUMBER_OF_IMAGES = 2

    class Meta:
        model = Review
        fields = ["id", "product", "rating", "review_text", "photos", "name", "email", "created_at", "updated_at"]

    def validate_photos(self, photos):
        # Don't allow images more than MAX_NUMBER_OF_IMAGES
        if len(photos) > self.MAX_NUMBER_OF_IMAGES:
            raise serializers.ValidationError(gettext("Can add utmost %s images" % self.MAX_NUMBER_OF_IMAGES))
        return photos


class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source="product", read_only=True)

    class Meta:
        model = CartItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="cartitem_set", many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "session_key", "user", "created_at", "items", "get_total_price", "free_cases"]


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    shipping = ShippingSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "cart", "shipping", "total_price", "delivery_charge", "order_status", "created_at", "updated_at"]

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.cart.is_order_created = True
        instance.cart.save()
        return instance


class OrderStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_items = serializers.IntegerField()
    last_week_total_orders_percentage = serializers.FloatField()
    last_week_total_items_percentage = serializers.FloatField()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_status', 'payment_method', 'payment_date', 'amount', 'transaction_id']


class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['id', 'order', 'status', 'updated_at', 'updated_by']


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_status', 'payment_method', 'payment_date', 'amount', 'transaction_id']


# class OrderSerializer(serializers.ModelSerializer):
#     tracking = OrderTrackingSerializer(many=True, read_only=True)
#     payment = PaymentSerializer(read_only=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'shipping', 'total_price', 'order_status', 'created_at', 'updated_at', 'tracking', 'payment']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'link'] 
