from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Exists, OuterRef, Count, Q

from . import models, serializers, utils


class StudentViewSet(viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["name", "admission_date"]
    ordering = ["name"]

    def get_queryset(self):
        today = timezone.localdate()

        return (
            super()
            .get_queryset()
            .annotate(
                count_on_progress=Count(
                    "sheet",
                    filter=Q(
                        sheet__is_finished=False,
                    ),
                    distinct=True,
                ),
                count_recorded=Count(
                    "sheet",
                    filter=Q(
                        sheet__is_finished=False,
                        sheet__record__created_at__date=today,
                    ),
                    distinct=True,
                ),
                count_finished=Count(
                    "sheet",
                    filter=Q(
                        sheet__is_finished=True,
                    ),
                    distinct=True,
                ),
            )
        )


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

    def get_queryset(self):
        today = timezone.localdate()

        return (
            super()
            .get_queryset()
            .annotate(
                is_recorded=Exists(
                    models.Record.objects.filter(
                        sheet=OuterRef("pk"),
                        created_at__date=today,
                    )
                )
            )
        )


class RecordViewSet(viewsets.ModelViewSet):
    queryset = models.Record.objects.all().order_by("-created_at")
    serializer_class = serializers.RecordSerializer
    filterset_fields = ["sheet__id"]
