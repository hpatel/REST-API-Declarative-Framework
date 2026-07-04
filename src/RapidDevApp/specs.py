"""Public and internal specification objects for miniapi."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

HookBefore = Callable[[Any], Any]
HookAfter = Callable[[Any, Any], Any]


class AuthType:
    """Supported authentication modes for MVP."""

    JWT = "jwt"
    NONE = "none"


@dataclass(slots=True)
class RouteHooks:
    """Optional route hooks.

    before hooks receive: ctx
    after hooks receive: ctx, result
    """

    before: list[HookBefore] = field(default_factory=list)
    after: list[HookAfter] = field(default_factory=list)


@dataclass(slots=True)
class RouteSpec:
    """Internal normalized route specification."""

    method: str
    path: str
    params: dict[str, type] = field(default_factory=dict)
    auth_type: str = AuthType.JWT
    permissions: list[str] = field(default_factory=list)
    hooks: RouteHooks = field(default_factory=RouteHooks)
    name: str | None = None


@dataclass(slots=True)
class Route:
    """Public developer-facing custom route definition.

    Use this with @routes(Route(...), Route(...)).
    """

    method: str
    path: str
    params: dict[str, type] = field(default_factory=dict)
    auth_type: str = AuthType.JWT
    permissions: list[str] = field(default_factory=list)
    before: list[HookBefore] = field(default_factory=list)
    after: list[HookAfter] = field(default_factory=list)
    name: str | None = None

    def __post_init__(self) -> None:
        if not self.method or not isinstance(self.method, str):
            raise ValueError("Route.method must be a non-empty string")
        if not self.path or not isinstance(self.path, str):
            raise ValueError("Route.path must be a non-empty string")
        if not self.path.startswith("/"):
            raise ValueError("Route.path must start with '/'")
        if self.auth_type not in {AuthType.JWT, AuthType.NONE}:
            raise ValueError("auth_type must be 'jwt' or 'none'")

    def to_spec(self) -> RouteSpec:
        return RouteSpec(
            method=self.method.upper(),
            path=self.path,
            params=dict(self.params or {}),
            auth_type=self.auth_type,
            permissions=list(self.permissions or []),
            hooks=RouteHooks(
                before=list(self.before or []),
                after=list(self.after or []),
            ),
            name=self.name,
        )


@dataclass(slots=True)
class ResourceSpec:
    """Internal normalized CRUD resource specification."""

    name: str
    model: type
    base_path: str
    id_param: str = "id"
    id_type: type = int
    exclude: set[str] = field(default_factory=set)
    auth_type: str = AuthType.JWT
    permissions: dict[str, list[str]] = field(default_factory=dict)
    hooks: dict[str, RouteHooks] = field(default_factory=dict)
