# accounts/management/commands/create_users.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction

APP_LABEL = "registration"   # <--- set this to the app label that defines CandidateProfile
MODEL_NAME = "candidateprofile"  # lowercase model name

class Command(BaseCommand):
    help = "Create/update bootstrap users and (optionally) run makemigrations + migrate. Enforces PO perms strictly."

    def add_arguments(self, parser):
        parser.add_argument("--po-username", default="PO", help="PO username (default: PO)")
        parser.add_argument("--po-password", default="PO", help="PO password (default: PO)")
        parser.add_argument("--admin-username", default="admin", help="Admin username (default: admin)")
        parser.add_argument("--admin-password", default="admin", help="Admin password (default: admin)")
        parser.add_argument(
            "--skip-makemigrations",
            action="store_true",
            help="Skip running `makemigrations` before migrate.",
        )
        parser.add_argument(
            "--skip-migrate",
            action="store_true",
            help="Skip running `migrate` before creating users.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        # 1) Run makemigrations (optional)
        if not options.get("skip_makemigrations"):
            self.stdout.write(self.style.NOTICE("Running makemigrations..."))
            try:
                call_command("makemigrations")
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"makemigrations failed: {exc}"))

        # 2) Run migrate (optional)
        if not options.get("skip_migrate"):
            self.stdout.write(self.style.NOTICE("Running migrate..."))
            try:
                call_command("migrate", "--noinput")
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"migrate failed: {exc}"))

        # Create/update PO user
        po_username = options["po_username"]
        po_password = options["po_password"]
        po_email = f"{po_username.lower()}@example.com"

        po_user, _ = User.objects.get_or_create(username=po_username, defaults={"email": po_email})
        po_user.set_password(po_password)
        po_user.is_active = True
        po_user.is_staff = True
        po_user.is_superuser = False
        try:
            po_user.role = User.Roles.PO_ADMIN
        except Exception:
            po_user.role = "PO_ADMIN"
        po_user.save()
        self.stdout.write(self.style.SUCCESS(f"Created/updated PO user: {po_user.username}"))

        # Create/get PO group and set EXACT permissions for CandidateProfile
        po_group_name = "PO"
        wanted_codenames = [f"view_{MODEL_NAME}", f"change_{MODEL_NAME}"]

        group, g_created = Group.objects.get_or_create(name=po_group_name)
        if g_created:
            self.stdout.write(self.style.SUCCESS(f"Created group: {po_group_name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"Using existing group: {po_group_name}"))

        perms_qs = Permission.objects.filter(content_type__app_label=APP_LABEL, codename__in=wanted_codenames)
        found = set(perms_qs.values_list("codename", flat=True))
        missing = [c for c in wanted_codenames if c not in found]
        if missing:
            self.stdout.write(self.style.WARNING(
                f"Missing permissions for app='{APP_LABEL}', model='{MODEL_NAME}': {missing}. "
                "Make sure migrations are applied before running this command."
            ))

        # Set group's permissions exactly (removes any other perms)
        group.permissions.set(list(perms_qs))
        self.stdout.write(self.style.SUCCESS(f"Group '{po_group_name}' permissions set to: {sorted(found)}"))

        # Remove PO user's other groups and direct permissions, then add only PO group
        po_user.groups.clear()
        po_user.user_permissions.clear()
        po_user.groups.add(group)
        self.stdout.write(self.style.SUCCESS(f"User '{po_user.username}' now only in group '{po_group_name}' and has no direct user_permissions."))

        # Create/update admin user
        admin_username = options["admin_username"]
        admin_password = options["admin_password"]
        admin_email = f"{admin_username.lower()}@example.com"

        admin_user, _ = User.objects.get_or_create(username=admin_username, defaults={"email": admin_email})
        admin_user.set_password(admin_password)
        admin_user.is_active = True
        admin_user.is_staff = True
        admin_user.is_superuser = True
        try:
            admin_user.role = User.Roles.CENTER_ADMIN
        except Exception:
            admin_user.role = "CENTER_ADMIN"
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"Created/updated admin user: {admin_user.username}"))

        self.stdout.write(self.style.MIGRATE_HEADING("Done."))
