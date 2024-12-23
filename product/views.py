from rest_framework import viewsets, response, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Product, Review, Wishlist, Cart, CartItem, ProductCategory
from .serializers import (
    ProductSerializer,
    ReviewSerializer,
    ReviewPhotoSerializer,
    CartSerializer,
    CartItemSerializer,
    ProductCategorySerializer
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for listing or retrieving products.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['post'], url_path='add-to-wishlist')
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

        return response.Response({'status': 'Product added to wishlist'}, status=status.HTTP_200_OK)


class ProductCatgeoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

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
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            # print(session_key, "ggggg")
            # if session_key:
            #     print(Cart.objects.values_list('session_key', flat=True))
            #     return Cart.objects.filter(session_key=session_key)
            return Cart.objects.all()

    def get_or_create_cart(self):
        """
        Ensure that a cart is created for the user or session if it doesn't exist.
        """
        if self.request.user.is_authenticated:
            # For authenticated users, associate the cart with the user
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            # For unauthenticated users, associate the cart with the session key
            session_key = self.request.session.__dict__
            print(session_key, "sssss")
            if not session_key:
                self.request.session.create()  # Ensure a session is created if not already present
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request, pk=None):
        """
        Adds a product to the cart.
        """
        # Get or create the cart
        cart = self.get_or_create_cart()

        # Fetch the product and quantity from the request data
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        quantity = int(request.data.get('quantity', 1))

        # Check if the cart already has this item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = quantity
        cart_item.save()

        return response.Response(
            {'message': 'Item added to cart successfully', 'total_quantity': cart_item.quantity},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def remove_from_cart(self, request, pk=None):
        """
        Removes a product from the cart.
        """
        cart = self.get_object()
        product = get_object_or_404(Product, id=request.data.get('product_id'))

        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.delete()

        return response.Response(
            {'message': 'Item removed from cart successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')

        if quantity <= 0:
            return response.Response({'error': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.quantity = quantity
        cart_item.save()

        return response.Response({'message': 'Quantity updated successfully', 'total_price': cart_item.get_total_price()})


class CartItemViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing CartItem instances.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
