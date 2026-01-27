#!/usr/bin/env python
"""
Management command to show help for exam administration commands
"""

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Show help for exam administration and cleanup commands'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🛠️  EXAM ADMINISTRATION COMMANDS"))
        self.stdout.write("=" * 70)
        
        self.stdout.write(self.style.WARNING("\n📊 DATA INSPECTION COMMANDS"))
        self.stdout.write("-" * 40)
        self.stdout.write("python manage.py show_data_stats")
        self.stdout.write("  Show current data statistics")
        self.stdout.write("  --detailed    Show detailed breakdown")
        
        self.stdout.write("\npython manage.py check_questions")
        self.stdout.write("  Check question data integrity")
        
        self.stdout.write(self.style.WARNING("\n🗑️  DATA CLEANUP COMMANDS"))
        self.stdout.write("-" * 40)
        
        self.stdout.write("1. QUESTIONS ONLY CLEANUP:")
        self.stdout.write("   python manage.py cleanup_exam_data --level=questions --confirm")
        self.stdout.write("   • Deletes: Questions, Question Papers, Uploads, Activations")
        self.stdout.write("   • Preserves: Users, Candidate Profiles, Exam Sessions, Results")
        self.stdout.write("   • Use when: You want to upload new questions but keep user data")
        
        self.stdout.write("\n2. EXAM DATA CLEANUP (RECOMMENDED):")
        self.stdout.write("   python manage.py cleanup_exam_data --level=exam-data --confirm")
        self.stdout.write("   • Deletes: Questions, Papers, Sessions, Results, Answers")
        self.stdout.write("   • Preserves: Users, Candidate Profiles")
        self.stdout.write("   • Use when: You want to reset exams but keep registered users")
        
        self.stdout.write("\n3. COMPLETE RESET:")
        self.stdout.write("   python manage.py cleanup_exam_data --level=everything --confirm")
        self.stdout.write("   • Deletes: Everything except superuser accounts")
        self.stdout.write("   • Preserves: Only superuser accounts")
        self.stdout.write("   • Use when: You want to start completely fresh")
        
        self.stdout.write("\n4. RESET EXAM SESSIONS ONLY:")
        self.stdout.write("   python manage.py reset_exam_sessions --confirm")
        self.stdout.write("   • Deletes: Exam Sessions, Candidate Answers")
        self.stdout.write("   • Preserves: Questions, Papers, Users")
        self.stdout.write("   • Use when: You want students to retake exams")
        self.stdout.write("   • Optional: --trade=OCC (reset only specific trade)")
        
        self.stdout.write(self.style.WARNING("\n🔧 SETUP COMMANDS"))
        self.stdout.write("-" * 40)
        self.stdout.write("python manage.py setup_trade_activations")
        self.stdout.write("  Set up trade paper activations")
        
        self.stdout.write("\npython manage.py import_questions sample_questions_upload.xlsx")
        self.stdout.write("  Import questions from Excel file")
        
        self.stdout.write("\npython manage.py create_users")
        self.stdout.write("  Create sample users and candidates")
        
        self.stdout.write(self.style.WARNING("\n🧪 TESTING COMMANDS"))
        self.stdout.write("-" * 40)
        self.stdout.write("python manage.py test_question_generation")
        self.stdout.write("  Test question generation for trades")
        
        self.stdout.write("\npython manage.py test_exam_flow")
        self.stdout.write("  Test complete exam flow")
        
        self.stdout.write(self.style.ERROR("\n⚠️  SAFETY NOTES"))
        self.stdout.write("-" * 40)
        self.stdout.write("• Always use --dry-run first to see what will be deleted")
        self.stdout.write("• Backup your database before running cleanup commands")
        self.stdout.write("• Use --confirm flag to actually execute deletions")
        self.stdout.write("• Superuser accounts are always preserved in 'everything' cleanup")
        
        self.stdout.write(self.style.SUCCESS("\n📋 TYPICAL WORKFLOWS"))
        self.stdout.write("-" * 40)
        
        self.stdout.write("🔄 RESET FOR NEW EXAM SESSION:")
        self.stdout.write("1. python manage.py show_data_stats")
        self.stdout.write("2. python manage.py reset_exam_sessions --dry-run")
        self.stdout.write("3. python manage.py reset_exam_sessions --confirm")
        
        self.stdout.write("\n🆕 UPLOAD NEW QUESTIONS:")
        self.stdout.write("1. python manage.py cleanup_exam_data --level=questions --dry-run")
        self.stdout.write("2. python manage.py cleanup_exam_data --level=questions --confirm")
        self.stdout.write("3. python manage.py import_questions new_questions.xlsx")
        self.stdout.write("4. python manage.py setup_trade_activations")
        
        self.stdout.write("\n🏁 COMPLETE FRESH START:")
        self.stdout.write("1. python manage.py show_data_stats")
        self.stdout.write("2. python manage.py cleanup_exam_data --level=everything --dry-run")
        self.stdout.write("3. python manage.py cleanup_exam_data --level=everything --confirm")
        self.stdout.write("4. python manage.py import_questions sample_questions_upload.xlsx")
        self.stdout.write("5. python manage.py setup_trade_activations")
        self.stdout.write("6. python manage.py create_users")
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("For more help on specific commands, use: python manage.py <command> --help"))