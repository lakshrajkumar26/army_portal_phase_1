from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from questions.models import QuestionPaper, ExamSession
from reference.models import Trade
from registration.models import CandidateProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Test question generation for exam sessions"

    def handle(self, *args, **options):
        # Get a candidate
        candidate = CandidateProfile.objects.first()
        if not candidate:
            self.stdout.write(self.style.ERROR("No candidates found"))
            return
        
        self.stdout.write(f"Testing with candidate: {candidate.name} ({candidate.trade})")
        
        # Get PRIMARY paper
        primary_paper = QuestionPaper.objects.filter(question_paper="PRIMARY").first()
        if not primary_paper:
            self.stdout.write(self.style.ERROR("No PRIMARY paper found"))
            return
        
        try:
            # Generate exam session
            session = primary_paper.generate_for_candidate(
                user=candidate.user,
                trade=candidate.trade
            )
            
            self.stdout.write(f"✓ Created session {session.id}")
            self.stdout.write(f"✓ Total questions: {session.total_questions}")
            
            # Check questions
            questions = session.questions
            self.stdout.write(f"✓ Questions retrieved: {questions.count()}")
            
            if questions.exists():
                first_q = questions.first()
                self.stdout.write(f"✓ First question: {first_q.question.text[:50]}...")
                self.stdout.write(f"✓ Question part: {first_q.question.part}")
                self.stdout.write(f"✓ Question marks: {first_q.question.marks}")
                
                # Check question distribution by part
                parts = {}
                for eq in questions:
                    part = eq.question.part
                    parts[part] = parts.get(part, 0) + 1
                
                self.stdout.write("Question distribution by part:")
                for part, count in sorted(parts.items()):
                    self.stdout.write(f"  Part {part}: {count}")
            
            self.stdout.write(self.style.SUCCESS("✓ Question generation test passed!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Question generation failed: {e}"))