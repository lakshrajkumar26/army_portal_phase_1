from django.core.management.base import BaseCommand
from questions.models import Question, ExamSession, ExamQuestion
from reference.models import Trade
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Check question distribution and exam sessions"

    def handle(self, *args, **options):
        # Check question distribution by part
        trade = Trade.objects.filter(code='OCC').first()
        if not trade:
            self.stdout.write(self.style.ERROR("OCC trade not found"))
            return
            
        self.stdout.write(f"Checking questions for trade: {trade}")
        
        self.stdout.write("\n=== PRIMARY Questions by Part ===")
        total_primary = 0
        for part in ['A', 'B', 'C', 'D', 'E', 'F']:
            count = Question.objects.filter(
                trade=trade, 
                paper_type='PRIMARY', 
                is_active=True, 
                part=part
            ).count()
            self.stdout.write(f"Part {part}: {count}")
            total_primary += count
        
        self.stdout.write(f"Total PRIMARY questions: {total_primary}")
        
        self.stdout.write("\n=== SECONDARY Questions by Part ===")
        total_secondary = 0
        for part in ['A', 'B', 'C', 'D', 'E', 'F']:
            count = Question.objects.filter(
                paper_type='SECONDARY', 
                is_common=True,
                is_active=True, 
                part=part
            ).count()
            self.stdout.write(f"Part {part}: {count}")
            total_secondary += count
        
        self.stdout.write(f"Total SECONDARY questions: {total_secondary}")
        
        # Check existing exam sessions
        self.stdout.write("\n=== Exam Sessions ===")
        sessions = ExamSession.objects.all()
        self.stdout.write(f"Total sessions: {sessions.count()}")
        
        for session in sessions:
            questions_count = session.questions.count()
            self.stdout.write(f"Session {session.id}: {questions_count} questions")
            if questions_count > 0:
                self.stdout.write(f"  First question: {session.questions.first().question.text[:50]}...")
            else:
                self.stdout.write("  No questions in this session!")
        
        # Check if there are any ExamQuestion entries
        exam_questions = ExamQuestion.objects.all()
        self.stdout.write(f"\nTotal ExamQuestion entries: {exam_questions.count()}")