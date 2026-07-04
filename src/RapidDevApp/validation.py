"""Basic path/query parameter validation for MVP."""

from __future__ import annotations

from uuid import UUID


def _bool_from_value(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "on"}:
            return True
        if lowered in {"false", "0", "no", "n", "off"}:
            return False
    raise ValueError(f"Cannot convert {value!r} to bool")


def convert_value(value, expected_type: type):
    """Convert one request value into the expected Python type."""

    if isinstance(value, expected_type):
        return value
    if expected_type is bool:
        return _bool_from_value(value)
    if expected_type is UUID:
        return UUID(str(value))
    return expected_type(value)


def validate_params(expected_params, path_params, query_params):
    """Validate and convert declared params.

    Declared params are searched first in Flask path variables, then in query args.
    Missing or invalid values raise werkzeug HTTP 400 errors.
    """

    from flask import abort

    validated = {}

    for name, expected_type in (expected_params or {}).items():
        if name in path_params:
            raw_value = path_params[name]
        elif name in query_params:
            raw_value = query_params[name]
        else:
            abort(400, description=f"Missing required parameter: {name}")

        try:
            validated[name] = convert_value(raw_value, expected_type)
        except Exception:
            abort(400, description=f"Invalid parameter type for: {name}")

    return validated
