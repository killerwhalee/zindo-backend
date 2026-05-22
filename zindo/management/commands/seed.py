import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from zindo.models import Record, Sheet, Student, TextBook


STUDENTS = [
    {"name": "김민준", "admission_date": datetime.date(2023, 3, 2)},
    {"name": "이서연", "admission_date": datetime.date(2023, 3, 2)},
    {"name": "박지호", "admission_date": datetime.date(2024, 3, 4)},
    {"name": "최수아", "admission_date": datetime.date(2024, 3, 4)},
    {"name": "정하은", "admission_date": datetime.date(2025, 3, 3)},
]

TEXTBOOKS = [
    {"name": "쎈 수학 3-1", "subject": "수학"},
    {"name": "쎈 수학 4-1", "subject": "수학"},
    {"name": "디딤돌 국어 독해력 3단계", "subject": "국어"},
    {"name": "디딤돌 국어 독해력 4단계", "subject": "국어"},
    {"name": "천재 과학 3", "subject": "과학"},
]

SHEETS = [
    # 김민준
    {"student": 0, "textbook": 0, "pace": 4},
    {"student": 0, "textbook": 2, "pace": 3},
    # 이서연
    {"student": 1, "textbook": 1, "pace": 4},
    {"student": 1, "textbook": 3, "pace": 3},
    # 박지호
    {"student": 2, "textbook": 0, "pace": 4},
    {"student": 2, "textbook": 4, "pace": 2},
    # 최수아
    {"student": 3, "textbook": 1, "pace": 4},
    # 정하은
    {"student": 4, "textbook": 2, "pace": 3},
]

# (sheet_index, start, end, days_ago, note)
RECORDS = [
    (0, 1, 4, 6, None),
    (0, 5, 8, 5, "곱셈 개념 이해 느림, 반복 필요"),
    (0, 9, 12, 4, None),
    (0, 13, 16, 3, None),
    (0, 17, 20, 2, "오늘 집중력 좋았음"),
    (0, 21, 24, 1, None),
    (1, 1, 3, 5, None),
    (1, 4, 6, 4, None),
    (1, 7, 9, 3, "지문 이해 잘 함"),
    (1, 10, 12, 1, None),
    (2, 1, 4, 4, None),
    (2, 5, 8, 3, None),
    (2, 9, 12, 2, None),
    (3, 1, 3, 3, "독해 속도 개선 중"),
    (3, 4, 6, 2, None),
    (4, 1, 4, 5, None),
    (4, 5, 8, 4, None),
    (4, 9, 12, 2, None),
    (6, 1, 4, 3, None),
    (6, 5, 8, 2, None),
    (7, 1, 3, 2, None),
]


class Command(BaseCommand):
    help = "Seed the database with dummy data for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing data before seeding",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            Record.objects.all().delete()
            Sheet.objects.all().delete()
            TextBook.objects.all().delete()
            Student.objects.all().delete()
            self.stdout.write("Flushed existing data.")

        students = [Student.objects.create(**s) for s in STUDENTS]
        self.stdout.write(f"Created {len(students)} students.")

        textbooks = [TextBook.objects.create(**t) for t in TEXTBOOKS]
        self.stdout.write(f"Created {len(textbooks)} textbooks.")

        sheets = [
            Sheet.objects.create(
                student=students[s["student"]],
                textbook=textbooks[s["textbook"]],
                pace=s["pace"],
            )
            for s in SHEETS
        ]
        self.stdout.write(f"Created {len(sheets)} sheets.")

        today = timezone.now()
        records = [
            Record.objects.create(
                sheet=sheets[r[0]],
                created_at=today - datetime.timedelta(days=r[3]),
                progress={"type": "range", "start": r[1], "end": r[2]},
                note=r[4],
            )
            for r in RECORDS
        ]
        self.stdout.write(f"Created {len(records)} records.")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
