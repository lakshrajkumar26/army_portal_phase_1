# questions/signals.py
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import QuestionUpload
from .services import (
    import_questions_from_dicts,
    is_encrypted_dat,
    decrypt_or_load_excel_bytes,
    load_questions_from_excel_data,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=QuestionUpload)
def import_on_upload(sender, instance, created, **kwargs):
    """
    Automatically import questions when a new QuestionUpload is saved.
    Also creates QuestionSetActivation entries for automatic trade-wise mapping.

    SAFE behavior:
    - Logs errors and returns (never crashes server)
    """
    if not created:
        return

    try:
        with instance.file.open("rb") as f:
            file_data = f.read()

        logger.info("Processing uploaded file: %s", instance.file.name)

        if not is_encrypted_dat(file_data):
            logger.error("File %s is not a valid .dat file", instance.file.name)
            return

        # Decrypt/Load Excel bytes
        try:
            excel_bytes = decrypt_or_load_excel_bytes(file_data, instance.decryption_password)
            logger.info("Successfully obtained Excel bytes from %s", instance.file.name)
        except Exception as e:
            logger.error("Decryption/load failed for %s: %s", instance.file.name, e)
            return

        # Parse Excel
        try:
            questions_data = load_questions_from_excel_data(excel_bytes)
            if not questions_data:
                logger.warning("No questions found in %s", instance.file.name)
                return
        except Exception as e:
            logger.error("Excel parse failed for %s: %s", instance.file.name, e)
            return

        # Import into DB
        try:
            created_count, skipped_count = import_questions_from_dicts(
                question_dicts=questions_data,
                forced_trade=None,
            )
            logger.info(
                "Imported from %s | created=%s skipped=%s",
                instance.file.name,
                created_count,
                skipped_count,
            )
            
            # Auto-create QuestionSetActivation entries for trade-wise mapping
            _create_question_set_activations(questions_data)
            
        except Exception as e:
            logger.error("DB import failed for %s: %s", instance.file.name, e)
            return

    except Exception as e:
        logger.error("Unexpected error processing %s: %s", instance.file.name, e)
        return


def _create_question_set_activations(questions_data):
    """
    Automatically create QuestionSetActivation entries based on uploaded questions.
    This enables automatic trade-wise QP mapping with sets.
    """
    from .models import QuestionSetActivation
    from reference.models import Trade
    
    try:
        # Extract unique combinations of trade, paper_type, and question_set from uploaded data
        unique_combinations = set()
        
        for q_data in questions_data:
            trade_name = q_data.get('trade', '').strip()
            paper_type = q_data.get('paper_type', 'PRIMARY').strip().upper()
            question_set = q_data.get('question_set', 'A').strip().upper()
            
            if trade_name and paper_type in ['PRIMARY', 'SECONDARY']:
                unique_combinations.add((trade_name, paper_type, question_set))
        
        # Create QuestionSetActivation entries
        created_activations = 0
        for trade_name, paper_type, question_set in unique_combinations:
            try:
                # Find the trade object
                trade = Trade.objects.filter(name__iexact=trade_name).first()
                if not trade:
                    logger.warning(f"Trade not found: {trade_name}")
                    continue
                
                # Create or get the activation entry
                activation, created = QuestionSetActivation.objects.get_or_create(
                    trade=trade,
                    paper_type=paper_type,
                    question_set=question_set,
                    defaults={
                        'is_active': False,  # Don't auto-activate, let admin control
                        'activated_by': None
                    }
                )
                
                if created:
                    created_activations += 1
                    logger.info(f"Created QuestionSetActivation: {trade.name} - {paper_type} - Set {question_set}")
                    
            except Exception as e:
                logger.error(f"Failed to create activation for {trade_name}-{paper_type}-{question_set}: {e}")
        
        if created_activations > 0:
            logger.info(f"Auto-created {created_activations} QuestionSetActivation entries for trade-wise mapping")
            
    except Exception as e:
        logger.error(f"Failed to create question set activations: {e}")
