# questions/forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import QuestionUpload
from .services import decrypt_or_load_excel_bytes, load_questions_from_excel_data, import_questions_from_dicts


class QuestionUploadForm(forms.ModelForm):
    """
    Admin form for uploading encrypted .dat files.

    Supports:
    - Your converter format (AES-GCM)
    - Legacy office-encrypted dat (msoffcrypto)
    - Plain XLSX renamed to .dat
    """

    class Meta:
        model = QuestionUpload
        fields = ["file", "decryption_password"]

        help_texts = {
            "file": "Upload encrypted .dat file only.",
            "decryption_password": "Passphrase used by converter to encrypt/decrypt the .dat file.",
        }

    def clean(self):
        cleaned_data = super().clean()
        uploaded_file = cleaned_data.get("file")
        password = cleaned_data.get("decryption_password")

        if not uploaded_file:
            return cleaned_data

        try:
            dat_bytes = uploaded_file.read()
        except Exception:
            raise ValidationError("Unable to read uploaded .dat file.")

        uploaded_file.seek(0)

        try:
            excel_bytes = decrypt_or_load_excel_bytes(dat_bytes, password)
            question_dicts = load_questions_from_excel_data(excel_bytes)
        except ValidationError as e:
            raise ValidationError(str(e))

        if not question_dicts:
            raise ValidationError("No valid questions found in the uploaded Excel.")

        return cleaned_data

    def save(self, commit=True):
        upload = super().save(commit=commit)

        uploaded_file = upload.file
        password = upload.decryption_password

        try:
            dat_bytes = uploaded_file.read()
            uploaded_file.seek(0)

            excel_bytes = decrypt_or_load_excel_bytes(dat_bytes, password)
            question_dicts = load_questions_from_excel_data(excel_bytes)

            created, skipped = import_questions_from_dicts(
                question_dicts=question_dicts,
                forced_trade=None,  # unified upload
            )

            upload._import_created = created
            upload._import_skipped = skipped

        except ValidationError:
            raise

        return upload
