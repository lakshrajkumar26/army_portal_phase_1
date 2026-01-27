"""
Management command to create PO (Personnel Officer) users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a PO (Personnel Officer) user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username for PO')
        parser.add_argument('--password', type=str, required=True, help='Password for PO')
        parser.add_argument('--email', type=str, default='', help='Email (optional)')
        parser.add_argument('--first-name', type=str, default='', help='First name (optional)')
        parser.add_argument('--last-name', type=str, default='', help='Last name (optional)')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options.get('email', '')
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'❌ User "{username}" already exists!'))
            return

        # Create PO user (staff but not superuser)
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,  # Can access admin
            is_superuser=False,  # Not a superuser
            role=User.Roles.PO_ADMIN  # Set role to PO_ADMIN
        )

        self.stdout.write(self.style.SUCCESS(f'✅ PO user created successfully!'))
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Name: {first_name} {last_name}')
        self.stdout.write(f'Role: PO_ADMIN')
        self.stdout.write(f'Can access admin: Yes')
        self.stdout.write(f'Is superuser: No')
        self.stdout.write('')
        self.stdout.write('Login at: http://127.0.0.1:8000/admin/')
