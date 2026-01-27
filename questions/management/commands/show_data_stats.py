#!/usr/bin/env python
"""
Management command to show current data statistics
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from questions.models import Question, QuestionPaper, ExamSession, TradePaperActivation, QuestionUpload
from results.models import CandidateAnswer
from registration.models import CandidateProfile
from reference.models import Trade
from django.db.models import Count, Q
import os
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Show current data statistics for the exam system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed breakdown by trade and question parts'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']

        self.stdout.write(self.style.SUCCESS("📊 EXAM SYSTEM DATA STATISTICS"))
        self.stdout.write("=" * 60)

        # User Statistics
        self.show_user_stats()
        
        # Question Statistics
        self.show_question_stats(detailed)
        
        # Exam Statistics
        self.show_exam_stats(detailed)
        
        # File Statistics
        self.show_file_stats()

    def show_user_stats(self):
        """Show user and registration statistics"""
        self.stdout.write(self.style.WARNING("\n👥 USER STATISTICS"))
        self.stdout.write("-" * 30)
        
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        regular_users = total_users - superusers
        
        total_candidates = CandidateProfile.objects.count()
        
        self.stdout.write(f"Total Users: {total_users}")
        self.stdout.write(f"  - Superusers: {superusers}")
        self.stdout.write(f"  - Regular Users: {regular_users}")
        self.stdout.write(f"Candidate Profiles: {total_candidates}")
        
        # Candidates by trade
        if total_candidates > 0:
            trade_stats = CandidateProfile.objects.values('trade__name').annotate(
                count=Count('id')
            ).order_by('-count')
            
            self.stdout.write("\nCandidates by Trade:")
            for stat in trade_stats:
                trade_name = stat['trade__name'] or 'No Trade'
                self.stdout.write(f"  - {trade_name}: {stat['count']}")

    def show_question_stats(self, detailed=False):
        """Show question and paper statistics"""
        self.stdout.write(self.style.WARNING("\n📝 QUESTION STATISTICS"))
        self.stdout.write("-" * 30)
        
        total_questions = Question.objects.count()
        active_questions = Question.objects.filter(is_active=True).count()
        
        self.stdout.write(f"Total Questions: {total_questions}")
        self.stdout.write(f"Active Questions: {active_questions}")
        
        if total_questions > 0:
            # Questions by part
            part_stats = Question.objects.values('part').annotate(
                count=Count('id')
            ).order_by('part')
            
            self.stdout.write("\nQuestions by Part:")
            for stat in part_stats:
                part_name = dict(Question.Part.choices).get(stat['part'], stat['part'])
                self.stdout.write(f"  - Part {stat['part']} ({part_name}): {stat['count']}")
            
            # Questions by paper type
            paper_type_stats = Question.objects.values('paper_type').annotate(
                count=Count('id')
            ).order_by('paper_type')
            
            self.stdout.write("\nQuestions by Paper Type:")
            for stat in paper_type_stats:
                self.stdout.write(f"  - {stat['paper_type']}: {stat['count']}")
            
            # Questions with/without options
            with_options = Question.objects.exclude(options__isnull=True).count()
            without_options = total_questions - with_options
            
            self.stdout.write(f"\nQuestions with options: {with_options}")
            self.stdout.write(f"Questions without options: {without_options}")
            
            if detailed:
                # Questions by trade
                trade_stats = Question.objects.values('trade__name').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                self.stdout.write("\nQuestions by Trade:")
                for stat in trade_stats:
                    trade_name = stat['trade__name'] or 'Common/No Trade'
                    self.stdout.write(f"  - {trade_name}: {stat['count']}")
        
        # Question Papers
        total_papers = QuestionPaper.objects.count()
        active_papers = QuestionPaper.objects.filter(is_active=True).count()
        
        self.stdout.write(f"\nQuestion Papers: {total_papers}")
        self.stdout.write(f"Active Papers: {active_papers}")
        
        # Trade Activations
        total_activations = TradePaperActivation.objects.count()
        active_activations = TradePaperActivation.objects.filter(is_active=True).count()
        
        self.stdout.write(f"\nTrade Activations: {total_activations}")
        self.stdout.write(f"Active Activations: {active_activations}")
        
        if active_activations > 0:
            activation_stats = TradePaperActivation.objects.filter(is_active=True).values(
                'trade__name', 'paper_type'
            ).annotate(count=Count('id'))
            
            self.stdout.write("\nActive Exam Configurations:")
            for stat in activation_stats:
                trade_name = stat['trade__name']
                paper_type = stat['paper_type']
                self.stdout.write(f"  - {trade_name}: {paper_type}")

    def show_exam_stats(self, detailed=False):
        """Show exam session and result statistics"""
        self.stdout.write(self.style.WARNING("\n🎯 EXAM STATISTICS"))
        self.stdout.write("-" * 30)
        
        total_sessions = ExamSession.objects.count()
        completed_sessions = ExamSession.objects.filter(completed_at__isnull=False).count()
        active_sessions = total_sessions - completed_sessions
        
        self.stdout.write(f"Total Exam Sessions: {total_sessions}")
        self.stdout.write(f"Completed Sessions: {completed_sessions}")
        self.stdout.write(f"Active Sessions: {active_sessions}")
        
        # Candidate Answers
        total_answers = CandidateAnswer.objects.count()
        self.stdout.write(f"Total Candidate Answers: {total_answers}")
        
        if detailed and total_sessions > 0:
            # Sessions by paper type
            session_stats = ExamSession.objects.values('paper__question_paper').annotate(
                count=Count('id')
            ).order_by('-count')
            
            self.stdout.write("\nSessions by Paper Type:")
            for stat in session_stats:
                paper_type = stat['paper__question_paper']
                self.stdout.write(f"  - {paper_type}: {stat['count']}")
            
            # Recent sessions
            recent_sessions = ExamSession.objects.order_by('-started_at')[:5]
            self.stdout.write("\nRecent Sessions:")
            for session in recent_sessions:
                status = "✅ Completed" if session.completed_at else "🔄 In Progress"
                self.stdout.write(f"  - {session.user.username}: {status} ({session.started_at.strftime('%Y-%m-%d %H:%M')})")

    def show_file_stats(self):
        """Show file system statistics"""
        self.stdout.write(self.style.WARNING("\n📁 FILE STATISTICS"))
        self.stdout.write("-" * 30)
        
        # Question uploads
        total_uploads = QuestionUpload.objects.count()
        self.stdout.write(f"Question Upload Records: {total_uploads}")
        
        # Check actual files
        try:
            media_root = settings.MEDIA_ROOT
            
            # Question files
            questions_path = os.path.join(media_root, 'uploads', 'questions')
            if os.path.exists(questions_path):
                question_files = len([f for f in os.listdir(questions_path) if os.path.isfile(os.path.join(questions_path, f))])
                self.stdout.write(f"Question Files on Disk: {question_files}")
            else:
                self.stdout.write("Question Files Directory: Not found")
            
            # Photo files
            photos_path = os.path.join(media_root, 'photos')
            if os.path.exists(photos_path):
                photo_files = len([f for f in os.listdir(photos_path) if os.path.isfile(os.path.join(photos_path, f))])
                self.stdout.write(f"Photo Files on Disk: {photo_files}")
            else:
                self.stdout.write("Photos Directory: Not found")
                
        except Exception as e:
            self.stdout.write(f"Could not check file system: {e}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📊 Statistics completed!"))