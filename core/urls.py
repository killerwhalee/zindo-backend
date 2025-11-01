from django.contrib import admin
from django.shortcuts import HttpResponse
from django.urls import include, path

urlpatterns = [
    # Admin page / healthchecker
    path("admin/", admin.site.urls),
    path("", lambda _: HttpResponse("zindo!")),
    # User app routing
    path("zindo/", include("zindo.urls")),
]
