import io
import json
import logging
import re
from typing import Dict, List, Optional, Tuple

import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from reference.models import Trade
from .models import Question

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
    """
    try:
        df = pd.read_excel(io.BytesIO(excel_bytes), engine="openpyxl")
    except Exception as e:
        raise ValidationError(f"File content is not a readable Excel file. Details: {e}")

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

        # Default logic:
        # - If paper_type column exists: use it
        # - Else infer: If trade == ALL => SECONDARY else PRIMARY
        trade_norm = _norm(trade_val)
        paper_type_norm = _norm(paper_type_val)

        if paper_type_norm in ("PRIMARY", "P"):
            paper_type = "PRIMARY"
        elif paper_type_norm in ("SECONDARY", "S"):
            paper_type = "SECONDARY"
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
        })

    return rows


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

            trade_norm = _norm(q.get("trade", ""))
            paper_type = _norm(q.get("paper_type", "")) or ("SECONDARY" if trade_norm == "ALL" else "PRIMARY")

            # Apply legacy forced_trade override if admin selected it
            trade_obj = None
            is_common = False

            if forced_trade:
                trade_obj = forced_trade
                # In forced legacy mode we can still mark ALL as common if the row explicitly says ALL
                if trade_norm == "ALL" or paper_type == "SECONDARY":
                    is_common = True
            else:
                if trade_norm == "ALL" or paper_type == "SECONDARY":
                    is_common = True
                    trade_obj = None
                else:
                    trade_obj = trade_lookup.get(trade_norm)

            # Avoid duplicates by text+part+trade/is_common
            exists_qs = Question.objects.filter(text=text, part=part)
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
                is_common=is_common,
                is_active=True,
            )
            created_count += 1

    return created_count, skipped_count
