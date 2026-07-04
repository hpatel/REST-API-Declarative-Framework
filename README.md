# RapidDevApp

RapidDevApp is a lightweight framework built on top of Flask and SQLAlchemy that enables rapid development of REST APIs using decorators. The aim of this framework is to provide all common functionality assocated with REST endpoints so the developers can focus on business logic.

The framework automatically generates CRUD endpoints, provides JWT-based authorization, supports route-level permissions, and allows developers to inject custom logic using hooks.

## Features

* Automatic CRUD endpoint generation
* Custom route definition using decorators
* JWT authentication support
* Permission-based authorization
* Before and after route hooks
* SQLAlchemy integration
* Flask integration
* Minimal boilerplate

---

# Installation

```bash
pip install flask sqlalchemy flask-sqlalchemy flask-jwt-extended
```

---

# Quick Start

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from RapidDevApp import (
    MiniApi,
    AuthType,
    Route,
    routes,
    resource,
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = \
    "postgresql://postgres:password@localhost/dev-db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

api = MiniApi(app, db.session)
```

---

# Custom Routes

Use `@routes(...)` when you need full control over endpoint behavior.

```python
from RapidDevApp import Route, routes, AuthType

@routes(
    Route(
        method="GET",
        path="/orders/<int:order_id>",
        params={"order_id": int},
        auth_type=AuthType.JWT,
        permissions=["orders:read"],
    )
)
def get_order(ctx, order_id):
    return {
        "order_id": order_id
    }
```

Register the route:

```python
api.register_function(get_order)
```

---

# Multiple Routes on a Single Function

```python
from uuid import UUID

@routes(
    Route(
        method="GET",
        path="/products/<uuid:product_id>",
        params={"product_id": UUID},
        permissions=["products:read"],
    ),
    Route(
        method="DELETE",
        path="/products/<uuid:product_id>",
        params={"product_id": UUID},
        permissions=["products:delete"],
    ),
)
def product_endpoint(ctx, product_id):
    if ctx.method == "GET":
        return get_product(product_id)

    if ctx.method == "DELETE":
        return delete_product(product_id)
```

---

# Resource CRUD Generation

Use `@resource(...)` to automatically generate CRUD endpoints for a SQLAlchemy model.

```python
@resource(
    name="users",
    model=User,
    auth_type=AuthType.JWT,
)
class UserResource:
    pass

api.register_resource(UserResource)
```

Generated endpoints:

```text
POST   /users
GET    /users
GET    /users/<id>
PATCH  /users/<id>
PUT    /users/<id>
DELETE /users/<id>
```

---

# Excluding Endpoints

```python
@resource(
    name="users",
    model=User,
    exclude={"DELETE"},
)
class UserResource:
    pass
```

Generated endpoints:

```text
POST   /users
GET    /users
GET    /users/<id>
PATCH  /users/<id>
PUT    /users/<id>
```

---

# Route Hooks

Hooks allow custom code to run before and after route execution.

```python
def before(ctx):
    ctx.query_params["loaded"] = True

def after(ctx, result):
    result["hooked"] = True
    return result

@routes(
    Route(
        method="GET",
        path="/hooked",
        auth_type=AuthType.NONE,
        before=[before],
        after=[after],
    )
)
def hooked(ctx):
    return {"ok": True}
```

Hook execution order:

```text
global before hooks
route before hooks
handler
route after hooks
global after hooks
```

---

# JWT Authorization

```python
Route(
    method="GET",
    path="/profile",
    auth_type=AuthType.JWT,
    permissions=["profile:read"],
)
```

Expected JWT claims:

```json
{
  "sub": "user_123",
  "permissions": [
    "profile:read"
  ]
}
```

---

# Authentication Types

```python
AuthType.JWT
AuthType.NONE
```

* `JWT` - Authentication required
* `NONE` - Public endpoint

---

# Request Context

Every handler receives a RequestContext object.

```python
def my_route(ctx):
    print(ctx.method)
    print(ctx.path_params)
    print(ctx.query_params)
    print(ctx.body)
    print(ctx.user)
```

---

# SQLAlchemy Models

RapidDevApp does not replace SQLAlchemy.

Developers continue to:

* Define SQLAlchemy models
* Configure database connections
* Manage migrations
* Define relationships

RapidDevApp handles:

* Route generation
* CRUD operations
* Authentication
* Authorization
* Validation
* Hooks

---

# Roadmap

Planned future features:

* OpenAPI / Swagger generation
* Request/response schemas
* Relationship expansion
* Query resources
* Filtering and sorting
* Pagination support
* Audit logging
* Soft deletes

```
```
