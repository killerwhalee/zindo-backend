import datetime
import uuid

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from . import models, serializers


def _send_verification_email(user):
    token, _ = models.EmailVerificationToken.objects.update_or_create(
        user=user,
        defaults={
            "token": uuid.uuid4(),
            "expires_at": timezone.now() + datetime.timedelta(hours=24),
        },
    )

    verify_url = f"{settings.API_BASE_URL}/user/auth/verify-email/?token={token.token}"
    send_mail(
        subject="[Zindo] 이메일 인증",
        message=f"아래 링크를 클릭하여 이메일을 인증하세요:\n\n{verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


class SignUpView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        _send_verification_email(user)

        return Response(
            {"detail": "Verification email has been sent."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        token_value = request.query_params.get("token")
        if not token_value:
            return Response(
                {"detail": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = models.EmailVerificationToken.objects.get(token=token_value)
        except models.EmailVerificationToken.DoesNotExist:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token.is_expired():
            return Response(
                {"detail": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = token.user
        user.is_active = True
        user.save()
        token.delete()

        return Response({"detail": "Email verified successfully."})


class SignInView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials or account not verified."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        generic_response = Response(
            {"detail": "Password reset email has been sent if the account exists."}
        )

        try:
            user = models.User.objects.get(email=email, is_active=True)
        except models.User.DoesNotExist:
            return generic_response

        token = models.PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + datetime.timedelta(hours=1),
        )

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token.token}"
        send_mail(
            subject="[Zindo] 비밀번호 재설정",
            message=f"아래 링크를 클릭하여 비밀번호를 재설정하세요:\n\n{reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return generic_response


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_value = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            token = models.PasswordResetToken.objects.get(
                token=token_value,
                is_used=False,
            )
        except models.PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or already used token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token.is_expired():
            return Response(
                {"detail": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = token.user
        user.set_password(password)
        user.save()

        token.is_used = True
        token.save()

        return Response({"detail": "Password has been reset successfully."})
