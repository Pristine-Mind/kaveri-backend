from rest_framework import viewsets, response, status, views
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import models
from datetime import timedelta
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    Product,
    Review,
    Wishlist,
    Cart,
    CartItem,
    ProductCategory,
    Shipping,
    Order,
    OrderTracking,
    Payment,
)
from .serializers import (
    ProductSerializer,
    ReviewSerializer,
    ReviewPhotoSerializer,
    CartSerializer,
    CartItemSerializer,
    ProductCategorySerializer,
    ShippingSerializer,
    OrderSerializer,
    OrderStatsSerializer,
    OrderTrackingSerializer,
    PaymentCreateSerializer,
)
from .email import send_order_status_email, send_payment_success_email


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for listing or retrieving products.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=["post"], url_path="add-to-wishlist")
    def add_to_wishlist(self, request, pk=None):
        """
        Custom action to add a product to the wishlist.
        If the user is authenticated, the product is added to their wishlist.
        If the user is not authenticated, a session-based wishlist is used.
        """

        product = get_object_or_404(Product, pk=pk)

        if request.user.is_authenticated:
            # If the user is authenticated, get or create a wishlist for the user
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        else:
            # If the user is not authenticated, use the session key to identify their wishlist
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            wishlist, created = Wishlist.objects.get_or_create(session_key=session_key)

        wishlist.products.add(product)

        return response.Response({"status": "Product added to wishlist"}, status=status.HTTP_200_OK)


class ProductCatgeoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filterset_fields = [
        "product",
    ]

    @action(detail=True, methods=["post"])
    def add_photo(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewPhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save()
            review.photos.add(photo)
            review.save()
            return response.Response({"message": "Photo added successfully."}, status=status.HTTP_201_CREATED)
        else:
            return response.Response(
                {"error": "Invalid data provided.", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class CartViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Cart instances.
    """

    # queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.is_authenticated
        if user_id:
            return Cart.objects.filter(user=user_id, is_order_created=False).order_by('-created_at')[:1]
        else:
            return Cart.objects.none()

        # print(self.request.user)
        # if self.request.user.is_authenticated:
        #     print("hreeeeee")
        #     return Cart.objects.filter(user=self.request.user)
        # else:
        #     session_key = self.request.session.session_key
        #     if session_key:
        #         return Cart.objects.filter(session_key=session_key)
        #     return Cart.objects.all()

    def get_or_create_cart(self):
        """
        Ensure that a cart is created for the user or session if it doesn't exist.
        """
        if self.request.user.is_authenticated:
            # For authenticated users, associate the cart with the user
            cart, created = Cart.objects.get_or_create(user=self.request.user, is_order_created=False)
        else:
            # For unauthenticated users, associate the cart with the session key
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()  # Ensure a session is created if not already present
                session_key = self.request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    @action(detail=False, methods=["post"])
    def add_to_cart(self, request, pk=None):
        """
        Adds a product to the cart.
        """
        # Get or create the cart
        cart = self.get_or_create_cart()

        # Fetch the product and quantity from the request data
        product = get_object_or_404(Product, id=request.data.get("product_id"))
        quantity = int(request.data.get("quantity", 1))

        # Check if the cart already has this item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = quantity
        cart_item.save()

        return response.Response(
            {"message": "Item added to cart successfully", "total_quantity": cart_item.quantity}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def remove_from_cart(self, request, pk=None):
        """
        Removes a product from the cart.
        """
        cart = self.get_or_create_cart()
        product_id = request.data.get("product_id")
        if not product_id:
            return response.Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.delete()

        return response.Response({"message": "Item removed from cart successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def update_quantity(self, request, pk=None):
        cart = self.get_or_create_cart()
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")

        if quantity <= 0:
            return response.Response({"error": "Quantity must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = get_object_or_404(CartItem, product=item_id, cart=cart)
        cart_item.quantity = quantity
        cart_item.save()

        return response.Response({"message": "Quantity updated successfully", "total_price": cart_item.get_total_price()})


class CartItemViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing CartItem instances.
    """

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class ShippingView(views.APIView):
    def post(self, request, *args, **kwargs):
        """Save shipping information for a cart."""
        serializer = ShippingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, cart_id):
        """Get shipping information for a specific cart."""
        try:
            shipping = Shipping.objects.get(cart_id=cart_id)
            serializer = ShippingSerializer(shipping)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Shipping.DoesNotExist:
            return response.Response({"detail": "Shipping information not found"}, status=status.HTTP_404_NOT_FOUND)


class OrderView(views.APIView):
    def post(self, request, *args, **kwargs):
        """Create an order from the cart and shipping details."""
        cart_id = request.data.get("cart_id")
        shipping_id = request.data.get("shipping_id")

        try:
            cart = Cart.objects.get(id=cart_id)
            shipping = Shipping.objects.get(id=shipping_id)
            from decimal import Decimal
            total_price = cart.get_total_price() + Decimal(request.data.get("delivery_charge", 0.0))

            order = Order.objects.create(
                cart=cart,
                shipping=shipping,
                total_price=total_price,
                delivery_charge=request.data.get("delivery_charge", 0.0),
                order_status="Pending",
            )
            cart.is_order_created = True
            cart.save()
            serializer = OrderSerializer(order)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        except (Cart.DoesNotExist, Shipping.DoesNotExist):
            return response.Response({"detail": "Invalid cart or shipping ID"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """Get details of an order."""
        try:
            order = Order.objects.get(id=kwargs["order_id"])
            serializer = OrderSerializer(order)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return response.Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class OrderStatsView(views.APIView):
    """
    View to retrieve the statistics for total orders, order items, returns orders, and fulfilled orders
    for the currently logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        last_week = today - timedelta(days=7)

        user_orders = Order.objects.filter(cart__user=request.user, created_at__gte=last_week)

        total_orders = user_orders.count()
        total_items = user_orders.aggregate(total_items=models.Sum('cart__cartitem__quantity'))['total_items'] or 0

        previous_week_start = last_week - timedelta(days=7)
        previous_week_end = last_week
        user_orders_last_week = Order.objects.filter(
            cart__user=request.user, created_at__range=[previous_week_start, previous_week_end]
        )
        total_orders_last_week = user_orders_last_week.count()
        total_items_last_week = user_orders_last_week.aggregate(
            total_items=models.Sum('cart__cartitem__quantity'))['total_items'] or 0

        def calculate_percentage_change(current, previous):
            if previous == 0:
                return 0
            return ((current - previous) / previous) * 100

        last_week_total_orders_percentage = calculate_percentage_change(total_orders, total_orders_last_week)
        last_week_total_items_percentage = calculate_percentage_change(total_items, total_items_last_week)

        data = {
            'total_orders': total_orders,
            'total_items': total_items,
            'last_week_total_orders_percentage': last_week_total_orders_percentage,
            'last_week_total_items_percentage': last_week_total_items_percentage,
        }
        serializer = OrderStatsSerializer(data)
        return response.Response(serializer.data)


class OrderReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for viewing orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.all()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(cart__user=self.request.user).order_by('-created_at')
        return queryset


class OrderTrackingViewSet(viewsets.ModelViewSet):
    queryset = OrderTracking.objects.all()
    serializer_class = OrderTrackingSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a new tracking entry for an order. This can be used by an admin
        to update the status of an order.
        """
        order_id = request.data.get('order')
        order = Order.objects.filter(id=order_id).first()

        if not order:
            return response.Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            send_order_status_email(order)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        Retrieves the order tracking history for a specific order.
        """
        order_id = request.query_params.get('order_id')
        if not order_id:
            return response.Response({"error": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.filter(id=order_id).first()
        if not order:
            return response.Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        tracking_entries = OrderTracking.objects.filter(order=order)
        serializer = self.get_serializer(tracking_entries, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            send_payment_success_email(payment)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
