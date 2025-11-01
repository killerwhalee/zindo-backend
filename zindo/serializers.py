from rest_framework import serializers

from . import models


class StudentSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()

    class Meta:
        model = models.Student
        fields = [
            "object",
            "id",
            "name",
            "birthday",
        ]

    def get_object(self, _):
        return "student"


class TextBookSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()

    class Meta:
        model = models.TextBook
        fields = [
            "object",
            "id",
            "name",
            "subject",
            "isbn",
            "image",
        ]

    def get_object(self, _):
        return "textbook"


class SheetSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()
    student = serializers.PrimaryKeyRelatedField(
        queryset=models.Student.objects.all(),
        write_only=True,
    )
    student_detail = StudentSerializer(
        source="student",
        read_only=True,
    )
    textbook = serializers.PrimaryKeyRelatedField(
        queryset=models.TextBook.objects.all(),
        write_only=True,
    )
    textbook_detail = TextBookSerializer(
        source="textbook",
        read_only=True,
    )

    class Meta:
        model = models.Sheet
        fields = [
            "object",
            "id",
            "student",
            "student_detail",
            "textbook",
            "textbook_detail",
            "pace",
            "is_finished",
        ]
        read_only_fields = [
            "student_detail",
            "textbook_detail",
        ]

    def get_object(self, _):
        return "sheet"


class RecordSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()
    sheet = serializers.PrimaryKeyRelatedField(
        queryset=models.Sheet.objects.all(),
        write_only=True,
    )
    sheet_detail = SheetSerializer(
        source="sheet",
        read_only=True,
    )

    class Meta:
        model = models.Record
        fields = [
            "object",
            "id",
            "sheet",
            "sheet_detail",
            "created_at",
            "progress",
            "note",
        ]

    def get_object(self, _):
        return "record"
