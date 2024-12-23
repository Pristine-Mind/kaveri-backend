from typing import Optional
from datetime import datetime
from tinymce.models import HTMLField
from django.db import models
from user.models import User


class ProductCategory(models.Model):
    """
    Represents a category for products, including an optional image.

    Attributes
    ----------
    name : str
        The name of the category.
    description : Optional[str]
        A brief description of the category.
    image : Optional[ImageField]
        An image representing the category.
    """

    name: str = models.CharField(
        max_length=50, unique=True, verbose_name="Category Name", help_text="The name of the product category."
    )
    description: Optional[str] = models.TextField(
        blank=True, null=True, verbose_name="Category Description", help_text="A brief description of the category."
    )
    image: Optional[models.ImageField] = models.ImageField(
        upload_to="category_images/",
        blank=True,
        null=True,
        verbose_name="Category Image",
        help_text="An image representing the category.",
    )

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Represents a product available for sale on the website.

    Attributes
    ----------
    name : str
        The name of the product.
    description : str
        A detailed description of the product.
    price : float
        The price of the product.
    category : str
        The category of the product. Possible values include:
        'adapters', 'data_cables', 'earbuds', 'headphones', 'power_banks', 'speakers'.
    stock_status : bool
        Availability of the product in stock.
    image : ImageField
        An image representing the product.
    featured : bool
        Indicates if the product is featured on the website.
    """

    name: str = models.CharField(max_length=255, verbose_name="Product Name", help_text="The name of the product.")
    description: str = HTMLField(verbose_name="Description", help_text="A detailed description of the product.")
    price: float = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Price", help_text="The price of the product."
    )
    category: ProductCategory = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Category",
        help_text="The category to which the product belongs.",
    )
    stock: int = models.IntegerField(verbose_name="stock", help_text="Available quantity of the product")
    stock_status: bool = models.BooleanField(
        default=True, verbose_name="In Stock", help_text="Indicates if the product is available in stock."
    )
    image: Optional[models.ImageField] = models.ImageField(
        upload_to="products/", verbose_name="Product Image", help_text="An image of the product."
    )
    featured: bool = models.BooleanField(
        default=False, verbose_name="Featured Product", help_text="Indicates if the product is featured on the website."
    )

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            The name of the product.
        """
        return self.name


class Review(models.Model):
    """
    Represents a review for a product.

    Attributes
    ----------
    product : Product
        The product being reviewed.
    rating : int
        The rating given to the product (1-5).
    review_text : str
        The text review of the product.
    photos : Optional[ImageField]
        Optional photos attached to the review.
    name : str
        The name of the reviewer.
    email : str
        The email address of the reviewer.
    created_at : datetime
        The date and time when the review was created.
    updated_at : datetime
        The date and time when the review was last updated.
    """

    product: "Product" = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Product",
        help_text="The product being reviewed.",
    )
    rating: int = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)], verbose_name="Your Rating", help_text="The rating given to the product (1-5)."
    )
    review_text: str = models.TextField(max_length=2000, verbose_name="Review", help_text="The text review of the product.")
    photos: Optional[models.ManyToManyField] = models.ManyToManyField(
        "ReviewPhoto",
        blank=True,
        related_name="reviews",
        verbose_name="Add photos",
        help_text="Optional photos attached to the review.",
    )
    name: str = models.CharField(max_length=100, verbose_name="Your name", help_text="The name of the reviewer.")
    email: str = models.EmailField(verbose_name="Your email", help_text="The email address of the reviewer.")
    created_at: "datetime" = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At", help_text="The date and time when the review was created."
    )
    updated_at: "datetime" = models.DateTimeField(
        auto_now=True, verbose_name="Updated At", help_text="The date and time when the review was last updated."
    )

    def __str__(self) -> str:
        return f"Review of {self.product.name} by {self.name}"


class ReviewPhoto(models.Model):
    """
    Represents a photo attached to a review.

    Attributes
    ----------
    image : ImageField
        The image file for the review photo.
    uploaded_at : datetime
        The date and time when the photo was uploaded.
    """

    image: models.ImageField = models.ImageField(
        upload_to="review_photos/", verbose_name="Review Photo", help_text="The image file for the review photo."
    )
    uploaded_at: "datetime" = models.DateTimeField(
        auto_now_add=True, verbose_name="Uploaded At", help_text="The date and time when the photo was uploaded."
    )

    def __str__(self) -> str:
        return f"Photo {self.id} for review"


class Wishlist(models.Model):
    """
    Represents a wishlist, which can belong to either a registered user or an anonymous session.
    A wishlist can contain multiple products.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wishlists', null=True, blank=True,
        verbose_name="User"
    )
    session_key = models.CharField(max_length=255, null=True, blank=True, verbose_name="Session Key")
    products = models.ManyToManyField(Product, related_name='wishlists', verbose_name="Products in Wishlist")

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Wishlist"
        return f"Wishlist for session {self.session_key}"

    class Meta:
        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"


class Cart(models.Model):
    """
    Represents a shopping cart that can be associated with a logged-in user or an anonymous session.

    Attributes:
        session_key (str): The session key for anonymous users.
        user (User): The user associated with the cart if logged in.
        created_at (datetime): The date and time when the cart was created.
    """
    session_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="Session Key")
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="User")
    created_at = models.DateTimeField(auto_now=True, verbose_name="Created At")

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        else:
            return f"Cart for session {self.session_key}"

    def get_total_price(self):
        """
        Calculates the total price of all items in the cart.

        Returns:
            float: The total price of all items in the cart.
        """
        return sum(item.get_total_price() for item in self.cartitem_set.all())


class CartItem(models.Model):
    """
    Represents an item in the shopping cart.

    Attributes:
        cart (Cart): The cart to which this item belongs.
        product (Product): The product being added to the cart.
        quantity (int): The quantity of the product being added.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="Cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        """
        Calculates the total price for this cart item based on the product price and quantity.

        Returns:
            Decimal: The total price for this item.
        """
        return self.product.price * self.quantity
