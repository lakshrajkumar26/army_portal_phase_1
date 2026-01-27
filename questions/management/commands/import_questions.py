import os
import re
import json
import ast
from decimal import Decimal
from typing import Any, Optional, List, Dict

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from docx import Document
from django.utils.module_loading import import_string

from questions.models import Question
# your reference models (as used in your Question model)
from reference.models import Trade, Level, Skill, QF, Category

# ---------- helper utilities ----------
def _field_exists(model, fname):
    try:
        model._meta.get_field(fname)
        return True
    except Exception:
        return False

def find_or_create_ref(model, raw_value, create_missing=False):
    """Try to resolve a reference model (Trade/Level/etc) from name or pk.
       If create_missing=True and model has a 'name' field, it will create.
    """
    if raw_value is None:
        return None
    raw = str(raw_value).strip()
    if raw == "" or raw.lower() == "nan":
        return None

    # try pk if integer
    try:
        pk = int(raw)
        obj = model.objects.filter(pk=pk).first()
        if obj:
            return obj
    except Exception:
        pass

    # try a few likely fields
    for field in ("name", "title", "label"):
        if _field_exists(model, field):
            q = {f"{field}__iexact": raw}
            obj = model.objects.filter(**q).first()
            if obj:
                return obj

    # create if allowed and model supports 'name'
    if create_missing and _field_exists(model, "name"):
        try:
            return model.objects.create(name=raw)
        except Exception:
            return None

    return None

def parse_json_like(value: Any):
    """Try to parse JSON-like strings, python literal lists/dicts, or comma-separated lists."""
    if value is None:
        return None
    # if already a dict/list/boolean/number
    if isinstance(value, (dict, list, bool, int, float)):
        return value

    s = str(value).strip()
    if s == "" or s.lower() == "nan":
        return None

    # try json
    try:
        return json.loads(s)
    except Exception:
        pass
    # try python literal
    try:
        return ast.literal_eval(s)
    except Exception:
        pass
    # fallback: comma/pipe split to list
    if "," in s:
        return [it.strip() for it in s.split(",") if it.strip() != ""]
    if "|" in s:
        return [it.strip() for it in s.split("|") if it.strip() != ""]
    # single scalar
    return s

def normalize_options(raw):
    """Return JSON-friendly options. Accepts list or dict or string."""
    parsed = parse_json_like(raw)
    if parsed is None:
        return None
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, list):
        return {"choices": parsed}
    # string: maybe "A,B,C" or "A|B|C"
    if isinstance(parsed, str):
        parts = [p.strip() for p in re.split(r"[,\|;/]", parsed) if p.strip()]
        if len(parts) > 1:
            return {"choices": parts}
        return parsed
    return parsed

def normalize_answer(raw):
    parsed = parse_json_like(raw)
    if isinstance(parsed, (list, dict)):
        return parsed
    if isinstance(parsed, str):
        low = parsed.lower()
        if low in ("true", "false"):
            return low == "true"
        return parsed.strip()
    return parsed

# ---------- parsers ----------
def import_from_excel(path, create_missing=False, skip_existing=False, sheet_name=None):
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    required_cols = ["text", "part"]
    for c in required_cols:
        if c not in df.columns:
            raise CommandError(f"Excel must contain column '{c}'. Found columns: {list(df.columns)}")

    created = 0
    skipped = 0
    errors = []
    for i, row in df.iterrows():
        try:
            text = str(row.get("text", "")).strip()
            if not text or text.lower() == "nan":
                skipped += 1
                continue

            if skip_existing and Question.objects.filter(text__iexact=text).exists():
                skipped += 1
                continue

            part = str(row.get("part", "")).strip()
            marks = row.get("marks", 1)
            # convert marks to Decimal
            try:
                marks = Decimal(str(marks))
            except Exception:
                marks = Decimal("1")

            options = normalize_options(row.get("options", None))
            correct = normalize_answer(row.get("correct_answer", None))

            trade = find_or_create_ref(Trade, row.get("trade", None), create_missing)
            level = find_or_create_ref(Level, row.get("level", None), create_missing)
            skill = find_or_create_ref(Skill, row.get("skill", None), create_missing)
            qf = find_or_create_ref(QF, row.get("qf", None), create_missing)
            category = find_or_create_ref(Category, row.get("category", None), create_missing)

            Question.objects.create(
                text=text,
                part=part,
                marks=marks,
                options=options,
                correct_answer=correct,
                trade=trade,
                level=level,
                skill=skill,
                qf=qf,
                category=category,
            )
            created += 1
        except Exception as e:
            errors.append((i, str(e)))
    return created, skipped, errors

def import_from_docx(path, create_missing=False, skip_existing=False):
    doc = Document(path)
    # collect paragraphs, remove empties
    paras = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]

    items = []
    current = {"text": "", "options": None, "correct_answer": None, "part": None, "marks": None,
               "trade": None, "level": None, "skill": None, "qf": None, "category": None}

    def commit_current():
        if current["text"].strip():
            items.append(current.copy())
            # reset
            for k in current.keys():
                current[k] = "" if isinstance(current[k], str) else None

    label_map = {
        "options": re.compile(r"^options?:\s*", re.I),
        "answer": re.compile(r"^answer[s]?:\s*", re.I),
        "part": re.compile(r"^part:\s*", re.I),
        "marks": re.compile(r"^marks?:\s*", re.I),
        "trade": re.compile(r"^trade:\s*", re.I),
        "level": re.compile(r"^level:\s*", re.I),
        "skill": re.compile(r"^skill:\s*", re.I),
        "qf": re.compile(r"^qf:\s*", re.I),
        "category": re.compile(r"^category:\s*", re.I),
    }

    for p in paras:
        # new question detection: begins with Q or "Question" or "1." style
        if re.match(r"^(Q\d*[\.\)]\s*)", p, re.I) or p.lower().startswith("question"):
            # commit previous and start new
            commit_current()
            # initialize new
            current["text"] = re.sub(r"^(Q\d*[\.\)]\s*)", "", p, flags=re.I).strip()
            continue

        # check labeled lines
        matched = False
        for key, rx in label_map.items():
            if rx.match(p):
                value = rx.sub("", p).strip()
                if key == "answer":
                    current["correct_answer"] = value
                else:
                    current[key] = value
                matched = True
                break
        if matched:
            continue

        # options line starting with "A." or "1." etc treat as continuation of options
        if re.match(r"^[A-D]\.|^\d+\.", p):
            # append to options area
            if current.get("options"):
                current["options"] = f"{current['options']}\n{p}"
            else:
                current["options"] = p
            continue

        # otherwise append to text
        if current["text"]:
            current["text"] = f"{current['text']} {p}"
        else:
            current["text"] = p

    # commit last
    commit_current()

    # Now create Questions
    created = 0
    skipped = 0
    errors = []
    for idx, it in enumerate(items):
        try:
            text = (it.get("text") or "").strip()
            if not text:
                continue
            if skip_existing and Question.objects.filter(text__iexact=text).exists():
                skipped += 1
                continue

            part = (it.get("part") or "A").strip()
            marks = it.get("marks") or 1
            try:
                marks = Decimal(str(marks))
            except Exception:
                marks = Decimal("1")

            options = normalize_options(it.get("options"))
            correct = normalize_answer(it.get("correct_answer"))

            trade = find_or_create_ref(Trade, it.get("trade"), create_missing)
            level = find_or_create_ref(Level, it.get("level"), create_missing)
            skill = find_or_create_ref(Skill, it.get("skill"), create_missing)
            qf = find_or_create_ref(QF, it.get("qf"), create_missing)
            category = find_or_create_ref(Category, it.get("category"), create_missing)

            Question.objects.create(
                text=text,
                part=part,
                marks=marks,
                options=options,
                correct_answer=correct,
                trade=trade,
                level=level,
                skill=skill,
                qf=qf,
                category=category,
            )
            created += 1
        except Exception as e:
            errors.append((idx, str(e)))
    return created, skipped, errors

# ---------- management command ----------
class Command(BaseCommand):
    help = "Import questions from an Excel (.xlsx) or Word (.docx) file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to Excel (.xlsx) or Word (.docx) file")
        parser.add_argument("--sheet", type=str, default=None, help="Sheet name (for Excel)")
        parser.add_argument("--create-missing", action="store_true", help="Create missing Trade/Level/Skill/QF/Category by name")
        parser.add_argument("--skip-existing", action="store_true", help="Skip rows whose question text already exists in DB")

    def handle(self, *args, **options):
        path = options["file_path"]
        sheet = options.get("sheet")
        create_missing = options.get("create_missing", False)
        skip_existing = options.get("skip_existing", False)

        if not os.path.exists(path):
            raise CommandError("File does not exist: " + path)

        ext = os.path.splitext(path)[1].lower()
        with transaction.atomic():
            if ext in (".xlsx", ".xls"):
                created, skipped, errors = import_from_excel(path, create_missing=create_missing,
                                                             skip_existing=skip_existing, sheet_name=sheet)
            elif ext in (".docx",):
                created, skipped, errors = import_from_docx(path, create_missing=create_missing,
                                                            skip_existing=skip_existing)
            else:
                raise CommandError("Unsupported file type. Use .xlsx or .docx")

        self.stdout.write(self.style.SUCCESS(f"Created: {created}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped}"))
        if errors:
            self.stdout.write(self.style.ERROR(f"Errors ({len(errors)}):"))
            for idx, err in errors[:20]:
                self.stdout.write(f" - row/item {idx}: {err}")
            if len(errors) > 20:
                self.stdout.write(f" ... {len(errors)-20} more errors (see logs).")
