"""Small SQLAlchemy serialization helpers."""

from __future__ import annotations

from typing import Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


def serialize(obj: Any):
    """Serialize basic SQLAlchemy model objects and common Python values."""

    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, (UUID, Decimal)):
        return str(obj)
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, (list, tuple, set)):
        return [serialize(item) for item in obj]

    # SQLAlchemy mapped class: use columns only, not relationships.
    table = getattr(obj, "__table__", None)
    if table is not None:
        return {column.name: getattr(obj, column.name) for column in table.columns}

    if hasattr(obj, "to_dict"):
        return obj.to_dict()

    return obj


def model_to_dict(obj: Any) -> dict[str, Any]:
    result = serialize(obj)
    if not isinstance(result, dict):
        raise TypeError("Expected serializable model object to become a dict")
    return result
