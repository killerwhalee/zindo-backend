from rest_framework import serializers

from . import models, utils

import datetime


class StudentSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    is_recorded = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = models.Student
        fields = [
            "object",
            "id",
            "name",
            "grade",
            "is_recorded",
        ]
        read_only_fields = [
            "object",
            "id",
            "grade",
        ]

    def get_object(self, _):
        return "student"

    def get_grade(self, obj):
        days = (datetime.date.today() - obj.admission_date).days
        grade = int(days / 365.25) + 1

        return grade


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
        read_only_fields = [
            "object",
            "id",
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
    isbn = serializers.CharField(
        write_only=True,
    )
    textbook_detail = TextBookSerializer(
        source="textbook",
        read_only=True,
    )
    is_recorded = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = models.Sheet
        fields = [
            "object",
            "id",
            "student",
            "student_detail",
            "isbn",
            "textbook_detail",
            "pace",
            "is_recorded",
            "is_finished",
        ]
        read_only_fields = [
            "object",
            "id",
            "student_detail",
            "textbook_detail",
        ]

    def validate(self, data):
        """Check isbn and convert into correct textbook object

        This validator validates isbn by following process:

        1. Check if textbook with given isbn exists on database.
        2. If not, call book search API and fetch book data from it.
        3. If book search was successful, create new textbook and return.
        4. If book search was not successful, raise validation error.

        Then, validator validates textbook selected by:

        1. Check if active sheet with given textbook already exists.

        It is possible to review the same book.
        So it is allowed to write sheet with the same book if the former book was finished.
        """

        # Pop isbn from payload. It will be converted into `textbook` later
        isbn = data.pop("isbn", None)

        # Skip textbook validation if request is partial and
        # does not contain isbn for field.
        if isbn is None and self.partial:
            return data

        # Check if textbook with given isbn exists on database
        if (qs := models.TextBook.objects.filter(isbn=isbn)).exists():
            textbook = qs.first()

        # If not, call book search API with given isbn
        else:
            search_res = utils.search_book(isbn)

            # Raise error if no books were found,
            # or something goes wrong with API
            if not search_res:
                raise serializers.ValidationError(
                    "No books were found with given isbn.",
                )

            # Pop unnecessary fields
            for key in ["object", "id"]:
                search_res.pop(key, None)

            # Create new textbook using fetched data and add to data
            textbook = models.TextBook.objects.create(**search_res)

        # Add textbook fields to data.
        data["textbook"] = textbook

        # Check textbook is already exists in active sheet.
        student = data["student"]

        print(textbook, student)

        if models.Sheet.objects.filter(
            student=student,
            textbook=textbook,
            is_finished=False,
        ).exists():
            raise serializers.ValidationError(
                "Active sheet already exists with given textbook.",
            )

        return data

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
        read_only_fields = [
            "object",
            "id",
        ]

    def get_object(self, _):
        return "record"
