from rest_framework import serializers

from . import models, utils


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
    isbn = serializers.CharField(
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
            "isbn",
            "textbook_detail",
            "pace",
            "is_finished",
        ]
        read_only_fields = [
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
        """

        # Pop isbn from payload. It will be converted into `textbook` later
        isbn = data.pop("isbn")

        # Check if textbook with given isbn exists on database
        if (qs := models.TextBook.objects.filter(isbn=isbn)).exists():
            data["textbook"] = qs.first()
            return data

        # If not, call book search API with given isbn
        search_res = utils.search_book(isbn)
        [search_res.pop(key) for key in ["object", "id"]]

        # Raise error if no books were found, or something goes wrong with API
        if not search_res:
            raise serializers.ValidationError(
                "No books were found with given isbn.",
            )

        # Create new textbook using fetched data and add to data
        textbook = models.TextBook.objects.create(**search_res)
        data["textbook"] = textbook

        return data

    def create(self, validated_data):
        print(validated_data)

        return super().create(validated_data)

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
