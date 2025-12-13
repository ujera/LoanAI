"""Helper functions and utilities."""

import json
from typing import Any, Dict, Optional
from uuid import uuid4

from loanai_agent.utils.logger import get_logger

logger = get_logger(__name__)


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for tracking."""
    return str(uuid4())


def safe_dict_get(data: Dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary with dot notation support."""
    keys = key.split(".")
    value = data
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default
        if value is None:
            return default
    return value


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    return f"${amount:,.2f}" if currency == "USD" else f"{amount:,.2f} {currency}"


def calculate_debt_to_income_ratio(
    monthly_income: float, monthly_debt: float
) -> float:
    """Calculate debt-to-income ratio."""
    if monthly_income <= 0:
        return 0.0
    return round((monthly_debt / monthly_income) * 100, 2)


def calculate_savings_rate(income: float, expenses: float) -> float:
    """Calculate savings rate as percentage."""
    if income <= 0:
        return 0.0
    return round(((income - expenses) / income) * 100, 2)


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def merge_dicts(base: Dict, updates: Dict, deep: bool = True) -> Dict:
    """Merge updates dict into base dict."""
    if not deep:
        return {**base, **updates}

    result = base.copy()
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_dicts(result[key], value, deep=True)
        else:
            result[key] = value
    return result


def to_json(data: Any, indent: Optional[int] = 2) -> str:
    """Convert data to JSON string."""
    try:
        return json.dumps(data, indent=indent, default=str)
    except Exception as e:
        logger.error(f"Error converting to JSON: {e}")
        return "{}"


def from_json(data: str) -> Dict:
    """Parse JSON string to dictionary."""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        return {}


def calculate_age(birth_year: int) -> int:
    """Calculate age from birth year."""
    from datetime import datetime

    current_year = datetime.now().year
    return current_year - birth_year


def normalize_phone(phone: str) -> str:
    """Normalize phone number by removing non-digit characters."""
    return "".join(filter(str.isdigit, phone))


def is_valid_email(email: str) -> bool:
    """Simple email validation."""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def round_to_nearest(value: float, nearest: float = 0.01) -> float:
    """Round value to nearest specified amount."""
    return round(value / nearest) * nearest
