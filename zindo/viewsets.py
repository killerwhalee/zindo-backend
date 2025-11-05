import environ
import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers

env = environ.Env()
env.read_env(settings.BASE_DIR / ".env")


class StudentViewSet(viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer


class TextBookViewSet(viewsets.ModelViewSet):
    queryset = models.TextBook.objects.all()
    serializer_class = serializers.TextBookSerializer

    @action(methods=["get"], detail=False)
    def search(self, *args, **kwargs):
        # Get isbn and check if exists
        if (isbn := self.request.query_params.get("isbn", None)) is None:
            return Response({})

        # Filter textbook and check if exists
        if (queryset := self.queryset.filter(isbn=isbn)).exists():
            serializer = serializers.TextBookSerializer(queryset.first())

            return Response(serializer.data)

        # If not, get book info externally
        else:
            # Build url, headers and query params
            url = "https://openapi.naver.com/v1/search/book.json"
            headers = {
                "X-Naver-Client-Id": env("NAVER_CLIENT_ID"),
                "X-Naver-Client-Secret": env("NAVER_CLIENT_SECRET"),
            }
            params = {"query": isbn}

            # Request search and retrieve results
            result = requests.get(url, params=params, headers=headers)
            items = result.json()["items"]

            if not items:
                return Response({})

            # Get first data from items and serializeU+
            item = items[0]
            data = {
                "object": "textbook",
                "id": None,
                "name": item["title"],
                "subject": None,
                "isbn": item["isbn"],
                "image": item["image"],
            }

            return Response(data)


class SheetViewSet(viewsets.ModelViewSet):
    queryset = models.Sheet.objects.all()
    serializer_class = serializers.SheetSerializer
    filterset_fields = ["student__id"]


class RecordViewSet(viewsets.ModelViewSet):
    queryset = models.Record.objects.all()
    serializer_class = serializers.RecordSerializer
    filterset_fields = ["sheet__id"]
