import io
import json
import logging
import re
import csv
from typing import Dict, List, Optional, Tuple

import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from reference.models import Trade
from .models import Question
from .csv_processor import QuestionCSVProcessor

logger = logging.getLogger(__name__)

# ============================================================
# Encryption format (matches your Converter crypto.ts)
# ============================================================
SALT_SIZE = 16
IV_SIZE = 12
KEY_LENGTH_BYTES = 32  # 256-bit
PBKDF2_ITERATIONS = 100000

def decrypt_or_load_excel_bytes(file_bytes: bytes, password: str) -> bytes:
    """
    Backward-compatible helper used by admin/forms.
    - If encrypted DAT → decrypt
    - If already Excel → return as-is
    """
    try:
        if is_encrypted_dat(file_bytes):
            return decrypt_dat_content(file_bytes, password)
        return file_bytes
    except Exception as e:
        raise ValueError(f"Unable to decrypt/load file: {e}")

def is_encrypted_dat(file_bytes: bytes) -> bool:
    """
    Your converter output format:
      [salt(16)][iv(12)][ciphertext+tag(variable)]
    So minimum length must be > 28 bytes.
    """
    return isinstance(file_bytes, (bytes, bytearray)) and len(file_bytes) > (SALT_SIZE + IV_SIZE)


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    if not passphrase:
        raise ValidationError("Decryption password is required.")
    if not salt or len(salt) != SALT_SIZE:
        raise ValidationError("Invalid .dat format (salt missing/corrupt).")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH_BYTES,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def decrypt_dat_content(file_bytes: bytes, passphrase: str) -> bytes:
    """
    Decrypt .dat produced by the Question Paper Converter (AES-GCM, PBKDF2 SHA-256).
    """
    if not is_encrypted_dat(file_bytes):
        raise ValidationError("Invalid .dat file format or file is too small.")

    salt = file_bytes[:SALT_SIZE]
    iv = file_bytes[SALT_SIZE:SALT_SIZE + IV_SIZE]
    encrypted_content = file_bytes[SALT_SIZE + IV_SIZE:]

    if len(iv) != IV_SIZE:
        raise ValidationError("Invalid .dat format (iv missing/corrupt).")

    key = _derive_key(passphrase, salt)

    try:
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(iv, encrypted_content, None)
        return decrypted
    except Exception as e:
        # Wrong password OR corrupted file
        raise ValidationError(f"Unable to decrypt .dat file. Check password. Details: {e}")


def decrypt_or_load_excel_bytes(file_bytes: bytes, passphrase: str) -> bytes:
    """
    Returns raw Excel bytes.
    - If bytes already look like Excel ZIP ('PK'), return as-is.
    - Else decrypt using AES-GCM format.
    """
    if isinstance(file_bytes, (bytes, bytearray)) and file_bytes[:2] == b"PK":
        return bytes(file_bytes)

    # Otherwise try decrypt
    decrypted = decrypt_dat_content(file_bytes, passphrase)

    # Excel xlsx is zip => 'PK'
    if decrypted[:2] != b"PK":
        raise ValidationError("Decrypted file content is not a readable Excel file.")
    return decrypted


# ============================================================
# Excel parsing
# ============================================================
def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip()).upper()


def load_questions_from_excel_data(excel_bytes: bytes) -> List[Dict]:
    """
    Reads Excel bytes and returns list of dicts for each question row.

    IMPORTANT:
    - Uses openpyxl engine explicitly to avoid pandas 'engine cannot be determined'.
    - Enhanced with comprehensive error handling and validation
    """
    if not excel_bytes:
        raise ValidationError("Excel file content is empty.")
    
    try:
        df = pd.read_excel(io.BytesIO(excel_bytes), engine="openpyxl")
    except Exception as e:
        raise ValidationError(f"File content is not a readable Excel file. Details: {e}")

    if df.empty:
        raise ValidationError("Excel file contains no data rows.")

    # Normalize columns
    df.columns = [str(c).strip() for c in df.columns]

    # Attempt to map common possible column names
    # You can adjust these mappings if your sheet uses different headings.
    col_map = {}
    for c in df.columns:
        uc = _norm(c)
        if uc in ("QUESTION", "QUESTIONS", "Q", "QNS", "QUESTION TEXT"):
            col_map["text"] = c
        elif uc in ("PART", "SECTION"):
            col_map["part"] = c
        elif uc in ("MARKS", "MARK", "SCORE"):
            col_map["marks"] = c
        elif uc in ("OPTION", "OPTIONS", "OPT"):
            col_map["options"] = c
        elif uc in ("CORRECT", "CORRECT ANSWER", "ANSWER", "ANS"):
            col_map["correct_answer"] = c
        elif uc in ("TRADE", "TRADE NAME"):
            col_map["trade"] = c
        elif uc in ("PAPER TYPE", "PAPER", "TYPE"):
            col_map["paper_type"] = c
        elif uc in ("QUESTION SET", "QUESTION_SET", "SET", "QS"):
            col_map["question_set"] = c
        elif uc in ("IS COMMON", "IS_COMMON", "COMMON"):
            col_map["is_common"] = c

    if "text" not in col_map:
        raise ValidationError("Excel must contain a Question column (e.g., 'Question').")

    rows: List[Dict] = []
    for _, r in df.iterrows():
        text = str(r.get(col_map["text"], "")).strip()
        if not text:
            continue

        part = str(r.get(col_map.get("part", ""), "A")).strip() if col_map.get("part") else "A"
        part = _norm(part)[:1] if part else "A"
        if part not in {"A", "B", "C", "D", "E", "F"}:
            part = "A"

        marks_val = r.get(col_map.get("marks", ""), 1) if col_map.get("marks") else 1
        try:
            marks = float(marks_val) if str(marks_val).strip() != "" else 1.0
        except Exception:
            marks = 1.0

        trade_val = str(r.get(col_map.get("trade", ""), "")).strip() if col_map.get("trade") else ""
        paper_type_val = str(r.get(col_map.get("paper_type", ""), "")).strip() if col_map.get("paper_type") else ""
        
        # Extract question_set
        question_set_val = str(r.get(col_map.get("question_set", ""), "A")).strip() if col_map.get("question_set") else "A"
        question_set = _norm(question_set_val)[:1] if question_set_val else "A"
        if question_set not in {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"}:
            # If question_set is not found in column, try to extract from question text
            import re
            set_match = re.search(r'Set ([A-Z])', text)
            if set_match:
                question_set = set_match.group(1)
            else:
                question_set = "A"
        
        # Extract is_common
        is_common_val = r.get(col_map.get("is_common", ""), False) if col_map.get("is_common") else False
        if isinstance(is_common_val, str):
            is_common = is_common_val.lower() in ('true', '1', 'yes', 'y')
        else:
            is_common = bool(is_common_val)

        # Enhanced logic with text-based SECONDARY detection:
        # 1. If paper_type column exists: use it
        # 2. If question text contains "SECONDARY": classify as SECONDARY
        # 3. Else infer: If trade == ALL => SECONDARY else PRIMARY
        trade_norm = _norm(trade_val)
        paper_type_norm = _norm(paper_type_val)

        if paper_type_norm in ("PRIMARY", "P"):
            paper_type = "PRIMARY"
        elif paper_type_norm in ("SECONDARY", "S"):
            paper_type = "SECONDARY"
        elif "SECONDARY" in text.upper():
            # Text-based SECONDARY detection - this is the critical fix
            paper_type = "SECONDARY"
            is_common = True  # Force is_common=True for text-detected secondary questions
            trade_norm = ""   # Force NULL trade for secondary questions
            logger.info(f"Text-based SECONDARY detection: '{text[:50]}...' classified as SECONDARY")
        else:
            paper_type = "SECONDARY" if trade_norm == "ALL" else "PRIMARY"

        # Options/correct answer: accept JSON strings OR raw text
        options_raw = r.get(col_map.get("options", ""), None) if col_map.get("options") else None
        correct_raw = r.get(col_map.get("correct_answer", ""), None) if col_map.get("correct_answer") else None

        options = _safe_json_or_text(options_raw)
        correct_answer = _safe_json_or_text(correct_raw)

        rows.append({
            "text": text,
            "part": part,
            "marks": marks,
            "options": options,
            "correct_answer": correct_answer,
            "trade": trade_norm,         # OCC / DMV / ALL etc.
            "paper_type": paper_type,    # PRIMARY / SECONDARY
            "question_set": question_set, # A, B, C, D, E, etc.
            "is_common": is_common,      # True/False
        })

    return rows


def load_questions_from_csv_data(csv_bytes: bytes) -> Tuple[List[Dict], List[str]]:
    """
    Process CSV data using the new QuestionCSVProcessor.
    Returns (questions_list, errors_list)
    """
    try:
        # Create a file-like object from bytes
        csv_file = io.BytesIO(csv_bytes)
        
        # Use the CSV processor
        processor = QuestionCSVProcessor(csv_file)
        success, questions_data = processor.validate_and_process()
        
        if success:
            # Create questions and return count
            created_count = processor.bulk_create_questions(questions_data)
            return [{"created": created_count}], []
        else:
            # Return errors for display
            return [], processor.errors
            
    except Exception as e:
        return [], [f"CSV processing error: {str(e)}"]


def detect_file_format(file_bytes: bytes) -> str:
    """
    Detect if the file is CSV or Excel format.
    Returns 'csv' or 'excel'
    """
    try:
        # Try to decode as text (CSV)
        text_content = file_bytes.decode('utf-8')
        # Simple heuristic: if it has comma-separated values and newlines, likely CSV
        lines = text_content.split('\n')
        if len(lines) > 1 and ',' in lines[0]:
            return 'csv'
    except UnicodeDecodeError:
        pass
    
    # If not CSV, assume Excel
    return 'excel'


def _safe_json_or_text(val):
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    # If looks like JSON
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except Exception:
            return s
    return s


# ============================================================
# Import into DB
# ============================================================
def import_questions_from_dicts(
    question_dicts: List[Dict],
    forced_trade: Optional[Trade] = None,
) -> Tuple[int, int]:
    """
    Creates Question rows.
    - forced_trade: legacy behavior (if QuestionUpload.trade was selected)
      If provided -> all questions get tagged with this trade (and treated as PRIMARY unless trade=ALL).
    """
    created_count = 0
    skipped_count = 0

    if not question_dicts:
        return 0, 0

    # Build lookup for trades by name (normalized)
    trades = Trade.objects.all()
    trade_lookup = {}
    for t in trades:
        trade_lookup[_norm(getattr(t, "name", ""))] = t
        # optional: also map code/slug if exist
        if hasattr(t, "code") and t.code:
            trade_lookup[_norm(t.code)] = t
        if hasattr(t, "slug") and t.slug:
            trade_lookup[_norm(t.slug)] = t

    with transaction.atomic():
        for q in question_dicts:
            text = (q.get("text") or "").strip()
            if not text:
                skipped_count += 1
                continue

            part = (q.get("part") or "A").strip().upper()[:1]
            if part not in {"A", "B", "C", "D", "E", "F"}:
                part = "A"

            marks = q.get("marks", 1)
            options = q.get("options")
            correct_answer = q.get("correct_answer")
            
            # Extract question_set and is_common from the data
            question_set = (q.get("question_set") or "A").strip().upper()[:1]
            if question_set not in {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"}:
                question_set = "A"
            
            is_common_from_data = q.get("is_common", False)

            # Enhanced classification logic with text-based SECONDARY detection
            trade_norm = _norm(q.get("trade", ""))
            paper_type = _norm(q.get("paper_type", ""))
            
            # Apply enhanced classification logic (same as in load_questions_from_excel_data)
            if paper_type in ("PRIMARY", "P"):
                paper_type = "PRIMARY"
            elif paper_type in ("SECONDARY", "S"):
                paper_type = "SECONDARY"
            elif "SECONDARY" in text.upper():
                # Text-based SECONDARY detection - this is the critical fix
                paper_type = "SECONDARY"
                logger.info(f"Text-based SECONDARY detection in import: '{text[:50]}...' classified as SECONDARY")
            else:
                paper_type = "SECONDARY" if trade_norm == "ALL" else "PRIMARY"

            # Apply legacy forced_trade override if admin selected it
            trade_obj = None
            is_common = False

            if forced_trade:
                trade_obj = forced_trade
                # In forced legacy mode we can still mark ALL as common if the row explicitly says ALL
                if trade_norm == "ALL" or paper_type == "SECONDARY" or is_common_from_data:
                    is_common = True
            else:
                # Enhanced logic: SECONDARY questions should have trade=NULL and is_common=True
                if paper_type == "SECONDARY" or "SECONDARY" in text.upper() or trade_norm == "ALL" or is_common_from_data:
                    is_common = True
                    trade_obj = None
                    # Force SECONDARY paper_type for consistency
                    if paper_type == "SECONDARY" or "SECONDARY" in text.upper():
                        paper_type = "SECONDARY"
                        logger.info(f"Data integrity check: SECONDARY question '{text[:30]}...' - trade=NULL, is_common=True, paper_type=SECONDARY")
                else:
                    trade_obj = trade_lookup.get(trade_norm)

            # Avoid duplicates by text+part+trade/is_common+question_set
            exists_qs = Question.objects.filter(text=text, part=part, question_set=question_set)
            if trade_obj:
                exists_qs = exists_qs.filter(trade=trade_obj)
            else:
                exists_qs = exists_qs.filter(trade__isnull=True)

            if exists_qs.exists():
                skipped_count += 1
                continue

            Question.objects.create(
                text=text,
                part=part,
                marks=marks,
                options=options,
                correct_answer=correct_answer,
                trade=trade_obj,
                paper_type=paper_type,
                question_set=question_set,
                is_common=is_common,
                is_active=True,
            )
            created_count += 1

    return created_count, skipped_count
