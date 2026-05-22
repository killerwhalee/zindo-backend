from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "name", "is_active", "is_staff", "date_joined"]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["email", "name"]
    ordering = ["-date_joined"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal", {"fields": ["name"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ]
            },
        ),
        ("Dates", {"fields": ["date_joined", "last_login"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "password1", "password2"],
            },
        ),
    ]
    readonly_fields = ["date_joined", "last_login"]


@admin.register(models.EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "created_at", "expires_at"]
    readonly_fields = ["token", "created_at"]


@admin.register(models.PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "created_at", "expires_at", "is_used"]
    readonly_fields = ["token", "created_at"]
