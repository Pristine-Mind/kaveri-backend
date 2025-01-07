from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import authenticate
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import views, response, status, viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    CustomResponseSerializer,
    ChangeRecoverPasswordSerializer,
    ChangePasswordSerializer,
    BeerClubMemberSerializer,
    ContactMessageSerializer,
    UserSerializer,
)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


def bad_request(message):
    return JsonResponse({"statusCode": 400, "message": message}, status=400)


@extend_schema(request=RegisterSerializer, responses=CustomResponseSerializer)
class RegistrationView(views.APIView):

    def post(self, request, version=None):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = {
            "success": True,
            "message": "User Registered Successfully",
            "errors": serializer.errors,
            "response_body": None,
        }
        response_serializer = CustomResponseSerializer(response_data)

        return response.Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(request=LoginSerializer, responses=CustomResponseSerializer)
class LoginView(views.APIView):

    def post(self, request):
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        user = authenticate(username=email, password=password)
        if not user.is_verified:
            return bad_request("Your aren't verified")
        if user is not None:
            api_key, created = Token.objects.get_or_create(user=user)
            if not created:
                api_key.created = timezone.now()
                api_key.save()

            data = {
                "token": api_key.key,
                "username": email,
                "first": user.first_name,
                "last": user.last_name,
                "expires": api_key.created + timedelta(7),
                "id": user.id,
            }

            response_data = {"success": True, "message": "User Logged Successfully", "errors": "", "response_body": data}

            response_serializer = CustomResponseSerializer(response_data)
            return response.Response(response_serializer.data, status=status.HTTP_200_OK)

        else:
            return bad_request("Invalid username or password")


class ChangeRecoverPasswordView(views.APIView):
    @extend_schema(request=ChangeRecoverPasswordSerializer, responses=None)
    def post(self, request, version=None):
        serializer = ChangeRecoverPasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(views.APIView):
    @extend_schema(request=ChangePasswordSerializer, responses=None)
    def post(self, request, version=None):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def beer_club_signup(request):
    if request.method == "POST":
        serializer = BeerClubMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def contact_message_create(request):
    if request.method == "POST":
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(
            {
                'user_id': self.user.id,
                'email': self.user.email,
                'is_verified': self.user.is_verified,
                'username': self.user.first_name + self.user.last_name,
            }
        )
        return data


class UserLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
