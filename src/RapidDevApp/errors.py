"""Consistent JSON error handling."""

from __future__ import annotations


def install_error_handlers(app):
    """Install JSON error responses on a Flask app."""

    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        from flask import jsonify

        response = jsonify(
            {
                "error": {
                    "code": error.name.lower().replace(" ", "_"),
                    "message": error.description,
                }
            }
        )
        response.status_code = error.code or 500
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        from flask import current_app, jsonify

        current_app.logger.exception("Unhandled exception", exc_info=error)
        response = jsonify(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "Internal server error",
                }
            }
        )
        response.status_code = 500
        return response
