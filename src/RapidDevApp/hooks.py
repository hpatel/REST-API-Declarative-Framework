"""Hook execution helpers."""

from __future__ import annotations


def run_before_hooks(ctx, hooks):
    """Run before hooks. Return first non-None response, otherwise None."""

    for hook in hooks:
        response = hook(ctx)
        if response is not None:
            return response
    return None


def run_after_hooks(ctx, result, hooks):
    """Run after hooks. A hook may replace result by returning non-None."""

    current = result
    for hook in hooks:
        modified = hook(ctx, current)
        if modified is not None:
            current = modified
    return current
