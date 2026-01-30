from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from faker import Faker
import random

from registration.models import CandidateProfile
from reference.models import Trade
from exams.models import Shift

User = get_user_model()
fake = Faker("en_IN")


class Command(BaseCommand):
    help = "Create dummy candidates with users (photograph kept NULL)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of dummy candidates to create"
        )

    def handle(self, *args, **options):
        count = options["count"]

        trades = list(Trade.objects.all())
        shifts = list(Shift.objects.all())

        if not trades:
            self.stdout.write(self.style.ERROR("❌ No trades found. Add trades first."))
            return

        created = 0
        attempts = 0

        while created < count and attempts < count * 3:
            attempts += 1

            army_no = f"ARMY{random.randint(100000, 999999)}"
            if CandidateProfile.objects.filter(army_no=army_no).exists():
                continue

            username = f"user_{army_no.lower()}"

            user = User.objects.create_user(
                username=username,
                password="Test@123"
            )

            trade = random.choice(trades)

            CandidateProfile.objects.create(
                user=user,

                # Personal
                army_no=army_no,
                rank=random.choice(["Sepoy", "Naik", "Havildar"]),
                unit=fake.word(),
                brigade=fake.word(),
                corps=fake.word(),
                command=fake.word(),
                trade=trade,

                name=fake.name(),
                dob=fake.date_of_birth(
                    minimum_age=18,
                    maximum_age=35
                ).strftime("%d-%m-%Y"),
                doe=fake.date_between(start_date="-10y", end_date="-1y"),
                father_name=fake.name_male(),

                # IDs (validators safe)
                aadhar_number=str(random.randint(10**11, 10**12 - 1)),
                mobile_no=str(random.randint(6000000000, 9999999999)),
                apaar_id=str(random.randint(10**11, 10**12 - 1)),

                # Photograph intentionally NULL

                # Exam / location
                nsqf_level=random.choice(["NSQF-3", "NSQF-4", "NSQF-5"]),
                exam_center=fake.city(),
                training_center=fake.city(),
                state=fake.state(),
                district=fake.city(),

                # Qualifications
                primary_qualification="10th",
                primary_duration="2 Years",
                primary_credits="20",

                secondary_qualification="12th",
                secondary_duration="2 Years",
                secondary_credits="30",

                # Exam slot
                shift=random.choice(shifts) if shifts else None,
                has_exam_slot=False,
            )

            created += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Created candidate {army_no}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 DONE: {created} dummy candidates created (photos = NULL)"
            )
        )
