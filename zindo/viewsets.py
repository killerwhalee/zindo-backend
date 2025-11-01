from rest_framework import viewsets

from . import models, serializers


class StudentViewSet(viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer


class TextBookViewSet(viewsets.ModelViewSet):
    queryset = models.TextBook.objects.all()
    serializer_class = serializers.TextBookSerializer


class SheetViewSet(viewsets.ModelViewSet):
    queryset = models.Sheet.objects.all()
    serializer_class = serializers.SheetSerializer
    filterset_fields = ["student__id"]


class RecordViewSet(viewsets.ModelViewSet):
    queryset = models.Record.objects.all()
    serializer_class = serializers.RecordSerializer
    filterset_fields = ["sheet__id"]
