# ShelfSense API Documentation

Base path for all endpoints: `/api/v1`

## Authentication

All endpoints except `POST /auth/register` and `POST /auth/login` require a JWT token in the `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | Public |
| POST | `/auth/login` | Login and get JWT tokens | Public |

## Users

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/users` | Get paginated list of users | Admin |
| POST | `/users` | Create a new user | Admin |
| GET | `/users/<id>` | Get a specific user | Admin |
| PUT | `/users/<id>` | Update a user | Admin |
| DELETE | `/users/<id>` | Delete a user | Admin |

## Categories

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/categories` | Get paginated list of categories | Admin, Manager, Staff |
| POST | `/categories` | Create a new category | Admin, Manager |
| GET | `/categories/<id>` | Get a specific category | Admin, Manager, Staff |
| PUT | `/categories/<id>` | Update a category | Admin, Manager |
| DELETE | `/categories/<id>` | Delete a category | Admin, Manager |

## Products

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/products` | Get paginated products. Query params: `?q=`, `?category_id=` | Admin, Manager, Staff |
| POST | `/products` | Create a new product | Admin, Manager |
| GET | `/products/<id>` | Get a specific product | Admin, Manager, Staff |
| PUT | `/products/<id>` | Update a product | Admin, Manager |
| DELETE | `/products/<id>` | Delete a product | Admin, Manager |
| POST | `/products/<id>/movements` | Log a stock movement. Body: `{"change_qty": 5, "reason": "restock"}` | Admin, Manager, Staff |
| GET | `/products/<id>/history` | Get paginated stock movement history for a product | Admin, Manager, Staff |

## Alerts & Notifications

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/restock-alerts` | Get products currently at or below their reorder threshold | Admin, Manager, Staff |
| GET | `/notifications` | Get paginated list of user's notifications | Admin, Manager, Staff |
| GET | `/notifications/stream` | Server-Sent Events (SSE) stream for real-time notifications | Admin, Manager, Staff |
| PATCH | `/notifications/<id>` | Mark a notification as read. Body: `{"is_read": true}` | Admin, Manager, Staff |

## Analytics

| Method | Endpoint | Description | Roles |
|---|---|---|---|
| GET | `/analytics/summary` | Get aggregated inventory stats | Admin, Manager, Staff |
| GET | `/analytics/trends` | Get daily stock movement totals. Query param: `?days=30` | Admin, Manager, Staff |
| GET | `/analytics/top-products` | Get top products. Query params: `?by=value` or `?by=movement` | Admin, Manager |
