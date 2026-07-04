"""CRUD route generation for @resource classes."""

from __future__ import annotations

from typing import Callable
from uuid import UUID

from .serializers import serialize
from .specs import RouteHooks, RouteSpec


_ACTION_METHODS = {
    "create": "POST",
    "list": "GET",
    "get": "GET",
    "patch": "PATCH",
    "put": "PUT",
    "delete": "DELETE",
}


def _is_excluded(resource, action: str) -> bool:
    method = _ACTION_METHODS[action]
    return method in resource.exclude or action.upper() in resource.exclude


def _converter_for(py_type: type) -> str:
    if py_type is int:
        return "int"
    if py_type is UUID:
        return "uuid"
    return "string"


def _id_path(resource) -> str:
    converter = _converter_for(resource.id_type)
    return f"{resource.base_path}/<{converter}:{resource.id_param}>"


def _permissions(resource, action: str) -> list[str]:
    return list(resource.permissions.get(action, []))


def _hooks(resource, action: str) -> RouteHooks:
    return resource.hooks.get(action, RouteHooks())


def _commit_or_rollback(db):
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def build_crud_routes(resource, db) -> list[tuple[RouteSpec, Callable]]:
    """Build RouteSpec/handler pairs for a ResourceSpec."""

    routes: list[tuple[RouteSpec, Callable]] = []

    if not _is_excluded(resource, "create"):
        routes.append(_make_create(resource, db))
    if not _is_excluded(resource, "list"):
        routes.append(_make_list(resource, db))
    if not _is_excluded(resource, "get"):
        routes.append(_make_get(resource, db))
    if not _is_excluded(resource, "patch"):
        routes.append(_make_patch(resource, db))
    if not _is_excluded(resource, "put"):
        routes.append(_make_put(resource, db))
    if not _is_excluded(resource, "delete"):
        routes.append(_make_delete(resource, db))

    return routes


def _spec(resource, action: str, method: str, path: str, params=None) -> RouteSpec:
    return RouteSpec(
        method=method,
        path=path,
        params=params or {},
        auth_type=resource.auth_type,
        permissions=_permissions(resource, action),
        hooks=_hooks(resource, action),
        name=f"{resource.name}.{action}",
    )

def _make_create(resource, db):
    spec = _spec(resource, "create", "POST", resource.base_path)

    def handler(ctx):
        from flask import abort

        if not isinstance(ctx.body, dict):
            abort(400, description="JSON body must be an object")

        obj = resource.model(**ctx.body)
        db.add(obj)
        _commit_or_rollback(db)
        try:
            db.refresh(obj)
        except Exception:
            # Some test doubles or sessions may not support refresh after commit.
            pass
        return serialize(obj)

    return spec, handler


def _make_list(resource, db):
    spec = _spec(resource, "list", "GET", resource.base_path)

    def handler(ctx):
        from sqlalchemy import select

        result = db.execute(select(resource.model))
        items = result.scalars().all()
        return serialize(items)

    return spec, handler


def _make_get(resource, db):
    spec = _spec(
        resource,
        "get",
        "GET",
        _id_path(resource),
        params={resource.id_param: resource.id_type},
    )

    def handler(ctx, **params):
        from flask import abort

        obj_id = params[resource.id_param]
        obj = db.get(resource.model, obj_id)
        if obj is None:
            abort(404, description=f"{resource.name} not found")
        return serialize(obj)

    return spec, handler


def _update_object_fields(obj, data: dict):
    for key, value in data.items():
        if hasattr(obj, key):
            setattr(obj, key, value)


def _make_patch(resource, db):
    spec = _spec(
        resource,
        "patch",
        "PATCH",
        _id_path(resource),
        params={resource.id_param: resource.id_type},
    )

    def handler(ctx, **params):
        from flask import abort

        if not isinstance(ctx.body, dict):
            abort(400, description="JSON body must be an object")

        obj_id = params[resource.id_param]
        obj = db.get(resource.model, obj_id)
        if obj is None:
            abort(404, description=f"{resource.name} not found")

        _update_object_fields(obj, ctx.body)
        _commit_or_rollback(db)
        try:
            db.refresh(obj)
        except Exception:
            pass
        return serialize(obj)

    return spec, handler


def _make_put(resource, db):
    spec = _spec(
        resource,
        "put",
        "PUT",
        _id_path(resource),
        params={resource.id_param: resource.id_type},
    )

    def handler(ctx, **params):
        from flask import abort

        if not isinstance(ctx.body, dict):
            abort(400, description="JSON body must be an object")

        obj_id = params[resource.id_param]
        obj = db.get(resource.model, obj_id)
        if obj is None:
            abort(404, description=f"{resource.name} not found")

        _update_object_fields(obj, ctx.body)
        _commit_or_rollback(db)
        try:
            db.refresh(obj)
        except Exception:
            pass
        return serialize(obj)

    return spec, handler


def _make_delete(resource, db):
    spec = _spec(
        resource,
        "delete",
        "DELETE",
        _id_path(resource),
        params={resource.id_param: resource.id_type},
    )

    def handler(ctx, **params):
        from flask import abort

        obj_id = params[resource.id_param]
        obj = db.get(resource.model, obj_id)
        if obj is None:
            abort(404, description=f"{resource.name} not found")

        db.delete(obj)
        _commit_or_rollback(db)
        return {"deleted": True, resource.id_param: obj_id}

    return spec, handler
