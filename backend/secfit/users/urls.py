from django.urls import path, include
from users import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("api/users/", views.UserList.as_view(), name="user-list"),
    path("api/users/verify/", views.VerifyEmail.as_view(), name="verify-email"),
    path("api/users/<int:pk>/", views.UserDetail.as_view(), name="user-detail"),
    path("api/users/two_factor/totp_uri/",
         views.TotpURI.as_view(), name="totp-uri"),
    path("api/users/two_factor/enable/",
         views.EnableTwoFactor.as_view(), name="enable-2fa"),
    path("api/users/two_factor/login/",
         views.LoginWithTOTP.as_view(), name="login-2fa"),
    path("api/users/<str:username>/",
         views.UserDetail.as_view(), name="user-detail"),
    path("api/offers/", views.OfferList.as_view(), name="offer-list"),
    path("api/offers/<int:pk>/", views.OfferDetail.as_view(), name="offer-detail"),
    path(
        "api/athlete-files/", views.AthleteFileList.as_view(), name="athlete-file-list"
    ),
    path(
        "api/athlete-files/<int:pk>/",
        views.AthleteFileDetail.as_view(),
        name="athletefile-detail",
    ),
    path("api/token/", views.LoginView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/remember_me/", views.RememberMe.as_view(), name="remember_me"),
    path("media/users/<int:athlete_id>/<str:filename>", views.AthleteFileResponse.as_view(), name="media_athlete_file")
]
