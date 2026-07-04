"""Decorators used by application developers."""

from __future__ import annotations

from typing import Callable

from .specs import AuthType, ResourceSpec, Route, RouteHooks


def routes(*route_defs: Route):
    #Attach one or more structured Route definitions to a function.

    def decorator(func: Callable):
        specs = []
        for route_def in route_defs:
            if not isinstance(route_def, Route):
                raise TypeError(
                    "@routes only accepts Route(...) objects. "
                    "Example: @routes(Route('GET', '/products'))"
                )
            specs.append(route_def.to_spec())

        setattr(func, "__miniapi_routes__", specs)
        return func

    return decorator


def resource(
    *,
    name: str,
    model: type,
    base_path: str | None = None,
    id_param: str = "id",
    id_type: type = int,
    exclude: set[str] | None = None,
    auth_type: str = AuthType.JWT,
    permissions: dict[str, list[str]] | None = None,
    hooks: dict[str, RouteHooks] | None = None,
):
    """Attach CRUD resource metadata to a class.

    Generated actions: create, list, get, patch, put, delete.
    Exclude can contain HTTP methods like {"DELETE"} or action names like {"delete"}.
    """

    def decorator(cls: type):
        if not name:
            raise ValueError("resource name is required")
        if model is None:
            raise ValueError("resource model is required")
        if auth_type not in {AuthType.JWT, AuthType.NONE}:
            raise ValueError("auth_type must be 'jwt' or 'none'")

        normalized_exclude = {item.upper() for item in (exclude or set())}
        spec = ResourceSpec(
            name=name,
            model=model,
            base_path=base_path or f"/{name}",
            id_param=id_param,
            id_type=id_type,
            exclude=normalized_exclude,
            auth_type=auth_type,
            permissions=permissions or {},
            hooks=hooks or {},
        )
        setattr(cls, "__miniapi_resource__", spec)
        return cls

    return decorator
