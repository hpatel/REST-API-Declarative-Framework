"""Request context passed to all handlers and hooks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RequestContext:
    method: str
    path: str
    route_name: str | None = None
    path_params: dict[str, Any] = field(default_factory=dict)
    query_params: dict[str, Any] = field(default_factory=dict)
    body: dict[str, Any] | list[Any] | None = None
    user: Any = None
    claims: dict[str, Any] | None = None
