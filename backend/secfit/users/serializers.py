from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model, password_validation
from users.models import Offer, AthleteFile, RememberMe, User
from django import forms
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .util import send_email_verification_mail
from django.core.validators import validate_email

class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password1 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "url",
            "id",
            "email",
            "username",
            "password",
            "password1",
            "athletes",
            "coach",
            "workouts",
            "coach_files",
            "athlete_files",
        ]
    def validate_email(self, value):
        try:
            validate_email(value)
        except forms.ValidationError as error:
            raise serializers.ValidationError(error.messages)
        return value

    def validate_username(self, value, MIN_LENGTH = 4):
        username = value
        if len(username) < MIN_LENGTH:
            raise serializers.ValidationError("Username must be at least {} characters".format(MIN_LENGTH))
        return value

    def validate_password(self, value):
        data = self.get_initial()

        password = data.get("password")
        password1 = data.get("password1")

        try:
            password_validation.validate_password(password)
        except forms.ValidationError as error:
            raise serializers.ValidationError(error.messages)

        if password != password1:
            raise serializers.ValidationError("Passwords must match!")

        return value

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password"]
        user_obj = get_user_model()(username=username, email=email)
        user_obj.set_password(password)
        user_obj.save()

        return user_obj


class UserGetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "url",
            "id",
            "email",
            "username",
            "athletes",
            "coach",
            "workouts",
            "coach_files",
            "athlete_files",
        ]


class UserPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["athletes"]

    def update(self, instance, validated_data):
        athletes_data = validated_data["athletes"]
        instance.athletes.set(athletes_data)

        return instance


class AthleteFileSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = AthleteFile
        fields = ["url", "id", "owner", "file", "athlete"]

    def create(self, validated_data):
        return AthleteFile.objects.create(**validated_data)


class OfferSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Offer
        fields = [
            "url",
            "id",
            "owner",
            "recipient",
            "status",
            "timestamp",
        ]

class LoginSerializer(TokenObtainSerializer):
    """
    Serializer for LoginView. Extends simplejwt's TokenObtainSerializer serializer
    """

    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials',
        'account_not_verified': 'This account is not verified. A new verification email has been sent.'
    }

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            send_email_verification_mail(self.user, self.context['request'])
            raise exceptions.AuthenticationFailed(
                self.error_messages['account_not_verified'],
                'account_not_verified',
            )

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data

class RememberMeSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for an RememberMe. Hyperlinks are used for relationships by default.

    Serialized fields: remember_me

    Attributes:
        remember_me:    Value of cookie used for remember me functionality
    """

    class Meta:
        model = RememberMe
        fields = ["remember_me"]

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']