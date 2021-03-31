import django
from rest_framework import mixins, generics, status, views
from workouts.mixins import CreateListModelMixin
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from users.serializers import (
    UserSerializer,
    OfferSerializer,
    AthleteFileSerializer,
    UserPutSerializer,
    UserGetSerializer,
    RememberMeSerializer,
    LoginSerializer,
    EmailVerificationSerializer,
    LoginWithTOTPSerializer,
)
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from users.models import Offer, AthleteFile
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from users.permissions import IsCurrentUser, IsAthlete, IsCoach, IsPostOrIsAuthenticated, IsOfferOwnerOrRecipient, IsOfferOwner, IsOfferRecipient, TwoFactorNotEnabled
from workouts.permissions import IsOwner, IsReadOnly
import json
from collections import namedtuple
import base64
import pickle
from django.core.signing import Signer
from .util import send_email_verification_mail, EmailVerificationToken, generateTwoFactorURI, generateQrCode, generateSecret
import pyotp
from django.http import FileResponse, Http404

# Create your views here.


class UserList(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsPostOrIsAuthenticated]

    def get(self, request, *args, **kwargs):
        self.serializer_class = UserGetSerializer
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = get_user_model().objects.get(username=user_data['username'])
        send_email_verification_mail(user, request)
        return Response(user_data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = get_user_model().objects.none()

        if self.request.user:
            # Return the currently logged in user
            status = self.request.query_params.get("user", None)
            if status and status == "current":
                qs = get_user_model().objects.filter(pk=self.request.user.pk)

        return qs


class UserDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    lookup_field_options = ["pk", "username"]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [permissions.IsAuthenticated &
                          (IsCurrentUser | IsReadOnly)]

    def get_object(self):
        for field in self.lookup_field_options:
            if field in self.kwargs:
                self.lookup_field = field
                break

        return super().get_object()

    def get(self, request, *args, **kwargs):
        self.serializer_class = UserGetSerializer
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.serializer_class = UserPutSerializer
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class OfferList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = OfferSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = Offer.objects.none()

        if self.request.user:
            qs = Offer.objects.filter(
                Q(owner=self.request.user) | Q(recipient=self.request.user)
            ).distinct()

            # filtering by status (if provided)
            status = self.request.query_params.get("status", None)
            if status is not None:
                qs = qs.filter(status=status)

            # filtering by category (sent or received)
            category = self.request.query_params.get("category", None)
            if category is not None:
                if category == "sent":
                    qs = qs.filter(owner=self.request.user)
                elif category == "received":
                    qs = qs.filter(recipient=self.request.user)

        return qs


class OfferDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [permissions.IsAuthenticated(), IsOfferOwnerOrRecipient()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated(), IsOfferRecipient()]
        if self.request.method in ['DELETE']:
            return [permissions.IsAuthenticated(), IsOfferOwner()]
        return []


class AthleteFileList(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    CreateListModelMixin,
    generics.GenericAPIView,
):
    queryset = AthleteFile.objects.all()
    serializer_class = AthleteFileSerializer
    permission_classes = [permissions.IsAuthenticated & (IsAthlete | IsCoach)]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = AthleteFile.objects.none()

        if self.request.user:
            qs = AthleteFile.objects.filter(
                Q(athlete=self.request.user) | Q(owner=self.request.user)
            ).distinct()

        return qs


class AthleteFileDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = AthleteFile.objects.all()
    serializer_class = AthleteFileSerializer
    permission_classes = [permissions.IsAuthenticated & (IsAthlete | IsOwner)]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class AthleteFileResponse(
    views.APIView
):
    permission_classes = [permissions.IsAuthenticated & (IsAthlete | IsOwner | IsCoach)]

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        
        path = f'{settings.MEDIA_ROOT}/{obj.file}'
        return FileResponse(open(path, 'rb'))

    
    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        try:
            obj = AthleteFile.objects.get(
                Q(athlete=self.kwargs['athlete_id']) & Q(file=f'users/{self.kwargs["athlete_id"]}/{self.kwargs["filename"]}')
            )
        except:
            raise Http404("Media does not exist")

        self.check_object_permissions(self.request, obj)

        return obj

# Allow users to save a persistent session in their browser


class RememberMe(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):

    serializer_class = RememberMeSerializer

    def get(self, request):
        if request.user.is_authenticated == False:
            raise PermissionDenied
        else:
            return Response({"remember_me": self.rememberme()})

    def post(self, request):
        cookieObject = namedtuple("Cookies", request.COOKIES.keys())(
            *request.COOKIES.values()
        )
        user = self.get_user(cookieObject)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )

    def get_user(self, cookieObject):
        decode = base64.b64decode(cookieObject.remember_me)
        user, sign = pickle.loads(decode)

        # Validate signature
        if sign == self.sign_user(user):
            return user

    def rememberme(self):
        creds = [self.request.user, self.sign_user(str(self.request.user))]
        return base64.b64encode(pickle.dumps(creds))

    def sign_user(self, username):
        signer = Signer()
        signed_user = signer.sign(username)
        return signed_user


class LoginView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = LoginSerializer


class VerifyEmail(generics.GenericAPIView):

    serializer_class = EmailVerificationSerializer

    def get(self, request):
        parsedToken = request.GET.get('token')
        try:
            token = EmailVerificationToken(parsedToken)
            user_id = token.get('user_id')
            user = get_user_model().objects.get(pk=user_id)
            if not user.is_verified:
                user.is_verified = True
                user.save()
                token.blacklist()
            return Response({'success': ['Successfully activated']}, status=status.HTTP_200_OK)
        except TokenError as identifier:
            return Response({'error': ['Token invalid or expired']}, status=status.HTTP_400_BAD_REQUEST)


class TotpURI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    # Generate URI used in QR for registering 2FA.
    # Save generated secret to for forther use. But secret not yet verified
    def get(self, request):
        user_id = request.user.pk
        user = get_user_model().objects.get(pk=user_id)
        secret = generateSecret()
        # If user has not set secret, set new secret
        if user.secret2fa is None:
            user.secret2fa = secret
            user.save()
        # If user already has secret, display existing secret
        else:
            secret = user.secret2fa
        return Response(generateTwoFactorURI(request.user, secret))


class EnableTwoFactor(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    # Accept user input: 6 digit token
    # Check if TOTP-token is correct
    # Return "Success" or "Wrong token"

    def post(self, request):
        # Get unverified secret from user
        user_id = request.user.pk
        user = get_user_model().objects.get(pk=user_id)
        secret = user.secret2fa
        # Set up reference to pyotp
        totp = pyotp.TOTP(secret)
        totp_code = request.data.get("totp_code")

        # Check if user inputed token is correct
        if (totp.verify(totp_code)):
            # Verify secret to user object
            try:
                user.is_verified_2fa = True
                user.save()
                return Response({'success': ['Successfully activated']}, status=status.HTTP_200_OK)
            except:
                return Response({'error': ['An error occured']}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': ['Token invalid or expired']}, status=status.HTTP_400_BAD_REQUEST)


class LoginWithTOTP(generics.GenericAPIView):
    # Check if TOTPVerificationToken is valid
    # Accept user input: 6 digit token
    # Check if TOTP-token is correct
    # Return "Success" or "Wrong code"

    serializer_class = LoginWithTOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
