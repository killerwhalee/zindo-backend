from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views, viewsets

router = DefaultRouter()
router.register("", viewsets.UserViewSet, basename="user")

urlpatterns = [
    path(
        "auth/",
        include(
            [
                path("signup/", views.SignUpView.as_view()),
                path("verify-email/", views.VerifyEmailView.as_view()),
                path("signin/", views.SignInView.as_view()),
                path("token/refresh/", TokenRefreshView.as_view()),
                path("password-reset/", views.PasswordResetRequestView.as_view()),
                path(
                    "password-reset/confirm/", views.PasswordResetConfirmView.as_view()
                ),
            ]
        ),
    ),
    *router.urls,
]
