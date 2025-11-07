from django.db import models
from django.core.exceptions import ValidationError
from . import utils


class Student(models.Model):
    name = models.CharField(
        "이름",
        max_length=8,
    )
    birthday = models.DateField(
        "생년월일",
        auto_now=False,
        auto_now_add=False,
    )

    def __str__(self):
        return f"[{self.__class__.__name__} #{self.id:04d}] {self.name}"


class TextBookManager(models.Manager):
    def create_from_isbn(self, isbn):
        # Check if textbook with given isbn exists on database
        if self.filter(isbn=isbn).exists():
            raise ValidationError(
                "Textbook with given isbn already exists.",
            )

        # If not, call book search API with given isbn
        search_res = utils.search_book(isbn)
        [search_res.pop(key, None) for key in ["object", "id"]]

        print(search_res)

        # Raise error if no books were found, or something goes wrong with API
        if not search_res:
            raise ValidationError(
                "No books were found with given isbn.",
            )

        # Create new textbook using fetched data and add to data
        textbook = self.create(**search_res)

        return textbook


class TextBook(models.Model):
    name = models.CharField(
        "교재명",
        max_length=32,
    )
    subject = models.CharField(
        "과목",
        max_length=8,
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        null=True,
        blank=True,
    )
    image = models.URLField(
        "교재 이미지 링크",
        max_length=200,
        null=True,
        blank=True,
    )

    objects = TextBookManager()

    def __str__(self):
        return f"[{self.__class__.__name__} #{self.id:04d}] {self.name} {self.subject}"


class Sheet(models.Model):
    student = models.ForeignKey(
        "zindo.Student",
        verbose_name="학생",
        on_delete=models.CASCADE,
    )
    textbook = models.ForeignKey(
        "zindo.TextBook",
        verbose_name="교재",
        on_delete=models.PROTECT,
    )

    pace = models.SmallIntegerField(
        "하루 목표 학습량",
        null=True,
        blank=True,
    )
    is_finished = models.BooleanField(
        "완료 여부",
        default=False,
    )

    def __str__(self):
        return f"[{self.__class__.__name__} #{self.id:04d}] {self.student.name} - {self.textbook.name}"


class Record(models.Model):
    sheet = models.ForeignKey(
        "zindo.Sheet",
        verbose_name="기록지",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(
        "학습일",
        auto_now=False,
        auto_now_add=True,
    )
    progress = models.JSONField(
        "진도상황",
    )
    note = models.TextField(
        "메모",
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"[{self.__class__.__name__} #{self.id:04d}] {self.sheet} {self.created_at}"
        )
