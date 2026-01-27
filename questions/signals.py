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
        except Exception as e:
            logger.error("DB import failed for %s: %s", instance.file.name, e)
            return

    except Exception as e:
        logger.error("Unexpected error processing %s: %s", instance.file.name, e)
        return
