# questions/apps.py

from django.apps import AppConfig


class QuestionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "questions"

    def ready(self):
        # Wire signals
        import questions.signals  # noqa

        # Auto-bootstrap core exam configuration (SAFE, idempotent)
        try:
            from django.db.utils import OperationalError, ProgrammingError
            from .models import QuestionPaper
            from reference.models import Trade
            from .models import TradePaperActivation

            # 1️⃣ Ensure base QuestionPaper rows exist
            QuestionPaper.objects.get_or_create(
                question_paper="PRIMARY",
                defaults={"is_active": False},
            )
            QuestionPaper.objects.get_or_create(
                question_paper="SECONDARY",
                defaults={"is_active": False},
            )

            # 2️⃣ Ensure TradePaperActivation rows exist for all trades
            for trade in Trade.objects.all():
                for paper_type in ("PRIMARY", "SECONDARY"):
                    TradePaperActivation.objects.get_or_create(
                        trade=trade,
                        paper_type=paper_type,
                        defaults={"is_active": False},
                    )

        except (OperationalError, ProgrammingError):
            # DB not ready (during migrate / first startup)
            pass
        except Exception:
            # Never crash production server
            pass
