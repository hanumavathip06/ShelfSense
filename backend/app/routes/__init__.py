from .auth import auth_bp
from .health import health_bp
from .categories import categories_bp
from .products import products_bp
from .alerts import alerts_bp
from .notifications import notifications_bp
from .analytics import analytics_bp
from .users import users_bp
from .forecast import forecast_bp
from .smart_reorder import smart_reorder_bp
from .imports import imports_bp
from .purchase_orders import po_bp
from .staff import staff_bp
from .manager import manager_bp
from .admin import admin_bp

__all__ = [
    'auth_bp',
    'health_bp',
    'categories_bp',
    'products_bp',
    'alerts_bp',
    'notifications_bp',
    'analytics_bp',
    'users_bp',
    'forecast_bp',
    'smart_reorder_bp',
    'imports_bp',
    'po_bp',
    'staff_bp',
    'manager_bp',
    'admin_bp'
]
