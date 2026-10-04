Entities: User, Category, Product, StockMovement, Notification

User: id, name, email, password_hash, role (admin | manager | staff), created_at
Category: id, name
Product: id, name, sku, category_id (FK), quantity, reorder_threshold, unit_price, supplier, created_at, updated_at
StockMovement: id, product_id (FK), change_qty, reason (sale | manual_adjustment | restock), performed_by (FK User), created_at
Notification: id, user_id (FK), type (low_stock | restock_created), message, is_read, created_at

Roles:
- admin: full access, manages users
- manager: full CRUD on products/categories/restock, no user management
- staff: read-only + can log stock movements, no delete

API base path: /api/v1
Auth: JWT in Authorization: Bearer header
All list endpoints: pagination via ?page=&limit=, filtering via query params