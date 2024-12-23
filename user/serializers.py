from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers

from .models import User, Recovery, BeerClubMember, ContactMessage


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]

    def validate_password(self, password) -> str:
        validate_password(password)
        return password

    def validate_email(self, email) -> str:
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("The email is already taken.")
        return email

    def save(self, **kwargs):
        with transaction.atomic():
            instance = User.objects.create_user(
                first_name=self.validated_data.get("first_name", ""),
                last_name=self.validated_data.get("last_name", ""),
                username=self.validated_data["email"],
                email=self.validated_data["email"],
                password=self.validated_data["password"],
                is_active=True,
            )
            return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)


class ChangeRecoverPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, new_password):
        validate_password(new_password)
        return new_password

    def validate(self, data):
        username = data["username"]
        token = data["token"]
        data["user"] = user = User.objects.filter(username__iexact=username).first()

        recovery = Recovery.objects.filter(user=user).first()
        if recovery is None:
            raise serializers.ValidationError("Could not authenticate")

        if recovery.token != token:
            return serializers.ValidationError("Could not authenticate")
        recovery.delete()
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "full_name",
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_old_password(self, password):
        user = self.context["request"].user
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid Old Password")
        return password

    def validate_new_password(self, password):
        validate_password(password)
        return password

    def save(self):
        self.is_valid(raise_exception=True)
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()


# TODO: Make this global response throught the code
class CustomResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(default="", max_length=255)
    errors = serializers.CharField(default="", allow_blank=True, required=False)
    response_body = serializers.JSONField(required=False, allow_null=True)

    def to_representation(self, instance):
        """
        Override this method if you need to control how the instance data
        is returned in the response.
        """
        return {
            "success": instance.get("success", True),
            "message": instance.get("message", ""),
            "errors": instance.get("errors", ""),
            "response_body": instance.get("response_body", None),
        }


class BeerClubMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeerClubMember
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'message', 'created_at']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
