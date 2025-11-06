from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers, utils


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
            data = utils.search_book(isbn)

            return Response(data)


class SheetViewSet(viewsets.ModelViewSet):
    queryset = models.Sheet.objects.all()
    serializer_class = serializers.SheetSerializer
    filterset_fields = ["student__id"]


class RecordViewSet(viewsets.ModelViewSet):
    queryset = models.Record.objects.all()
    serializer_class = serializers.RecordSerializer
    filterset_fields = ["sheet__id"]
