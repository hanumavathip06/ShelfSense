from flask import Flask
from .config import Config
from .extensions import db, migrate, cors, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    
    # Configure Flask-Migrate to use DIRECT_URL for schema migrations
    # We pass it through the engine options temporarily during migrations
    migrate.init_app(app, db)
    
    # Ensure database schema exists
    with app.app_context():
        try:
            from . import models
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Database schema auto-creation notice: {e}")
    
    cors.init_app(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGIN']}})
    jwt.init_app(app)
    
    @app.after_request
    def set_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none'"
        response.headers['Strict-Transport-Security'] = "max-age=31536000; includeSubDomains"
        response.headers['X-Content-Type-Options'] = "nosniff"
        response.headers['X-Frame-Options'] = "DENY"
        response.headers['Referrer-Policy'] = "strict-origin-when-cross-origin"
        return response

    # Register blueprints
    from .routes import (
        health_bp, auth_bp, categories_bp, products_bp,
        alerts_bp, notifications_bp, analytics_bp, users_bp,
        forecast_bp, smart_reorder_bp, imports_bp
    )

    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(categories_bp, url_prefix='/api/v1/categories')
    app.register_blueprint(products_bp, url_prefix='/api/v1/products')
    app.register_blueprint(alerts_bp, url_prefix='/api/v1')
    app.register_blueprint(notifications_bp, url_prefix='/api/v1/notifications')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(forecast_bp, url_prefix='/api/v1/forecast')
    app.register_blueprint(smart_reorder_bp, url_prefix='/api/v1/smart-reorder')
    app.register_blueprint(imports_bp, url_prefix='/api/v1/imports')
    
    from .routes import po_bp, staff_bp, manager_bp, admin_bp
    app.register_blueprint(po_bp, url_prefix='/api/v1/purchase-orders')
    app.register_blueprint(staff_bp, url_prefix='/api/v1/staff')
    app.register_blueprint(manager_bp, url_prefix='/api/v1/manager')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')

    if not app.config.get('TESTING') and not app.config.get('DEBUG') and not __import__('os').environ.get('DISABLE_SCHEDULER'):
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            pass

    return app
