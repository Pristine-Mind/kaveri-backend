"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, re_path as url, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from user import views as user_views
from product import views as product_views

router = DefaultRouter()
router.register(r"products", product_views.ProductViewSet, basename="product")
router.register(r"review", product_views.ReviewViewSet, basename="review")
router.register(r"cart", product_views.CartViewSet, basename="cart")
router.register(r"product-category", product_views.ProductCatgeoryViewSet, basename="product-category")
router.register(r'orders', product_views.OrderReadOnlyViewSet, basename='order')  # Register the readonly viewset


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    url(r"^api/register", user_views.RegistrationView.as_view()),
    url(r"^change_password", user_views.ChangePasswordView.as_view()),
    url(r"^change_recover_password", user_views.ChangeRecoverPasswordView.as_view()),
    url(r"^api/login", user_views.LoginView.as_view()),
    path("docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api-docs/", SpectacularAPIView.as_view(), name="schema"),
    path("api-docs/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('api/v1/beer-club/signup/', user_views.beer_club_signup, name='beer_club_signup'),
    path('api/v1/contact-us/signup/', user_views.contact_message_create, name='contact_message_create'),
    path("api/v1/shipping/", product_views.ShippingView.as_view(), name="shipping"),
    path("api/v1/shipping/<int:cart_id>/", product_views.ShippingView.as_view(), name="get-shipping"),
    path("api/v1/order/", product_views.OrderView.as_view(), name="create-order"),
    path("api/v1/order/<int:order_id>/", product_views.OrderView.as_view(), name="get-order"),
    path('api/token/', user_views.UserLoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/profile/', user_views.ProfileView.as_view(), name="profile"),
    path('api/order-stats/', product_views.OrderStatsView.as_view(), name='order-stats'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
