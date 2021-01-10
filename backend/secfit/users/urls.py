from django.urls import path, include
from users import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("api/users/", views.UserList.as_view(), name="user-list"),
    path("api/users/<int:pk>/", views.UserDetail.as_view(), name="user-detail"),
    path("api/users/<str:username>/", views.UserDetail.as_view(), name="user-detail"),
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
]
