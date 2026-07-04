"""miniapi MVP: decorators for rapid Flask + SQLAlchemy endpoint creation."""

from .context import RequestContext
from .decorators import resource, routes
from .registry import MiniApi
from .specs import AuthType, ResourceSpec, Route, RouteHooks, RouteSpec

__all__ = [
    "AuthType",
    "MiniApi",
    "RequestContext",
    "ResourceSpec",
    "Route",
    "RouteHooks",
    "RouteSpec",
    "resource",
    "routes",
]
