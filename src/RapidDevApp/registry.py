"""Flask registration engine for miniapi."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from .auth import apply_auth, check_permissions
from .context import RequestContext
from .crud import build_crud_routes
from .errors import install_error_handlers
from .hooks import run_after_hooks, run_before_hooks
from .validation import validate_params


class MiniApi:
    """Small framework facade.

    Example:
        api = MiniApi(app, db.session)
        api.register_function(my_handler)
        api.register_resource(ProductResource)
    """

    def __init__(self, app, db_session=None, *, install_errors: bool = True):
        self.app = app
        self.db = db_session
        self.global_before_hooks: list[Callable] = []
        self.global_after_hooks: list[Callable] = []

        if install_errors:
            install_error_handlers(app)

    def before_all(self, hook: Callable):
        self.global_before_hooks.append(hook)
        return hook

    def after_all(self, hook: Callable):
        self.global_after_hooks.append(hook)
        return hook

    def register_function(self, func: Callable):
        specs = getattr(func, "__miniapi_routes__", [])
        if not specs:
            raise ValueError(f"No @routes metadata found on {func.__name__}")

        for spec in specs:
            handler = self._build_handler(func, spec)
            endpoint_name = self._make_endpoint_name(func, spec)
            self.app.add_url_rule(
                spec.path,
                endpoint=endpoint_name,
                view_func=handler,
                methods=[spec.method],
            )

    def register_resource(self, resource_cls: type):
        if self.db is None:
            raise ValueError("db_session is required to register @resource CRUD classes")

        spec = getattr(resource_cls, "__miniapi_resource__", None)
        if spec is None:
            raise ValueError(f"No @resource metadata found on {resource_cls.__name__}")

        for route_spec, raw_handler in build_crud_routes(spec, self.db):
            handler = self._build_handler(raw_handler, route_spec)
            endpoint_name = f"resource.{self._safe_endpoint(route_spec.name or spec.name)}"
            self.app.add_url_rule(
                route_spec.path,
                endpoint=endpoint_name,
                view_func=handler,
                methods=[route_spec.method],
            )

    def _build_handler(self, func: Callable, spec):
        @wraps(func)
        def wrapper(**path_params):
            from flask import Response, jsonify, request

            ctx = RequestContext(
                method=spec.method,
                path=spec.path,
                route_name=spec.name,
                path_params=dict(path_params),
                query_params=request.args.to_dict(flat=True),
                body=request.get_json(silent=True),
            )

            validated_params = validate_params(spec.params, path_params, request.args)

            apply_auth(ctx, spec.auth_type)
            check_permissions(ctx, spec.permissions)

            early_response = run_before_hooks(ctx, self.global_before_hooks)
            if early_response is not None:
                return self._to_response(early_response)

            early_response = run_before_hooks(ctx, spec.hooks.before)
            if early_response is not None:
                return self._to_response(early_response)

            result = func(ctx, **validated_params)

            result = run_after_hooks(ctx, result, spec.hooks.after)
            result = run_after_hooks(ctx, result, self.global_after_hooks)

            if isinstance(result, Response):
                return result
            return jsonify({"data": result})

        return wrapper

    def _to_response(self, value):
        from flask import Response, jsonify

        if isinstance(value, Response):
            return value
        return jsonify(value)

    def _make_endpoint_name(self, func: Callable, spec) -> str:
        route_label = spec.name or f"{spec.method}.{spec.path}"
        return f"{func.__module__}.{func.__name__}.{self._safe_endpoint(route_label)}"

    @staticmethod
    def _safe_endpoint(value: str) -> str:
        return (
            value.replace("/", "_")
            .replace("<", "")
            .replace(">", "")
            .replace(":", "_")
            .replace(".", "_")
            .replace("-", "_")
            .strip("_")
        )
