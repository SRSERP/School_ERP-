import re
import datetime
from decimal import Decimal
from typing import Optional, Tuple, Any
from .models import Student


def normalize_text(text: Any) -> str:
    """
    Normalizes a text string by stripping leading/trailing whitespace,
    converting to lowercase, and collapsing multiple spaces into a single space.
    """
    if not text:
        return ""
    text_str = str(text).strip().lower()
    return re.sub(r'\s+', ' ', text_str)


def normalize_student_name(first_name: Any, last_name: Any = '') -> str:
    """
    Normalizes student full name.
    """
    f = str(first_name or '').strip()
    l = str(last_name or '').strip()
    return normalize_text(f"{f} {l}")


def normalize_parent_name(name: Any) -> str:
    """
    Normalizes father / parent / guardian name by stripping common prefixes/titles
    like Mr., Mr, Shri, Shri., Late, Smt., Dr., etc.
    """
    if not name:
        return ""
    text = normalize_text(name)
    prefixes = [
        'mr.', 'mr ', 'shri.', 'shri ', 'shree.', 'shree ',
        'late.', 'late ', 'smt.', 'smt ', 'dr.', 'dr ',
        'father:', 'father -', 'father-', 'father '
    ]
    for p in prefixes:
        if text.startswith(p):
            text = text[len(p):].strip()
            break
    return normalize_text(text)


def parse_date_of_birth(val: Any) -> Optional[datetime.date]:
    """
    Parses various date representations (datetime.date, datetime.datetime,
    Excel serial number integer/float, or strings in multiple formats) into a datetime.date object.
    """
    if not val:
        return None

    if isinstance(val, datetime.datetime):
        return val.date()

    if isinstance(val, datetime.date):
        return val

    # Handle numeric excel serial dates (e.g. 43100)
    if isinstance(val, (int, float)):
        try:
            # Excel base date is 1899-12-30
            base_date = datetime.date(1899, 12, 30)
            return base_date + datetime.timedelta(days=int(val))
        except Exception:
            pass

    val_str = str(val).strip()
    if not val_str:
        return None

    # Strip time part if present (e.g. "2018-04-12 00:00:00")
    date_part = val_str.split()[0].replace(',', '').strip()

    formats = (
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%d.%m.%Y',
        '%m/%d/%Y',
        '%m-%d-%Y',
        '%d %b %Y',
        '%d %B %Y',
    )
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_part, fmt).date()
        except (ValueError, TypeError):
            continue

    return None


def find_duplicate_student(
    first_name: Any,
    last_name: Any = '',
    father_name: Any = '',
    dob: Any = None,
    exclude_id: Optional[int] = None,
    school: Optional[Any] = None
) -> Optional[Student]:
    """
    Checks if a student already exists with the same:
    1. Student Name (First Name + Last Name, or single combined Name)
    2. Father Name (Parent / Guardian Name, normalized)
    3. Date of Birth (DOB)

    Returns the matching Student instance if found, else None.
    """
    if not (first_name or last_name) or not father_name or dob is None:
        return None

    parsed_dob = parse_date_of_birth(dob)
    if not parsed_dob:
        return None

    target_student_norm = normalize_student_name(first_name, last_name)
    target_father_norm = normalize_parent_name(father_name)

    if not target_student_norm or not target_father_norm:
        return None

    # Query students with the exact same date of birth (and school if provided)
    candidates = Student.objects.filter(dob=parsed_dob)
    if school:
        candidates = candidates.filter(school=school)
    if exclude_id:
        candidates = candidates.exclude(id=exclude_id)

    target_first_only = normalize_text(first_name)

    for student in candidates:
        s_student_norm = normalize_student_name(student.first_name, student.last_name)
        s_father_norm = normalize_parent_name(student.parent_name)

        # 1. Father name must match
        if s_father_norm != target_father_norm:
            continue

        # 2. Student name match:
        # Exact match of combined full names
        if s_student_norm == target_student_norm:
            return student

        # Or if one of them does not have a last name, check if first name matches
        s_first_only = normalize_text(student.first_name)
        has_last_target = bool(str(last_name or '').strip())
        has_last_student = bool(str(student.last_name or '').strip())

        if (not has_last_target or not has_last_student) and (target_first_only and target_first_only == s_first_only):
            return student

    return None


def get_row_field(row: dict, aliases: list, default: str = '') -> str:
    """
    Helper to extract a field value from an Excel/CSV row dictionary using multiple possible alias keys.
    """
    for alias in aliases:
        # Direct check
        if alias in row and row[alias] is not None:
            val = str(row[alias]).strip()
            if val:
                return val

        # Check with space replaced by underscore
        alias_us = alias.replace(' ', '_')
        if alias_us in row and row[alias_us] is not None:
            val = str(row[alias_us]).strip()
            if val:
                return val

        # Check with underscore replaced by space
        alias_sp = alias.replace('_', ' ')
        if alias_sp in row and row[alias_sp] is not None:
            val = str(row[alias_sp]).strip()
            if val:
                return val

    return default
