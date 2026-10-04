import os

# 1. Update models/__init__.py
models_init = "d:/Shashi/ShelfSense/backend/app/models/__init__.py"
with open(models_init, "r") as f:
    content = f.read()
if "ImportJob" not in content:
    content = content.replace("from .audit import AuditLog", "from .audit import AuditLog\nfrom .import_job import ImportJob")
    content = content.replace("'AuditLog'", "'AuditLog',\n    'ImportJob'")
    with open(models_init, "w") as f:
        f.write(content)

# 2. Add imports blueprint to app/__init__.py
app_init = "d:/Shashi/ShelfSense/backend/app/__init__.py"
with open(app_init, "r") as f:
    app_content = f.read()

if "imports_bp" not in app_content:
    app_content = app_content.replace(
        "forecast_bp, smart_reorder_bp",
        "forecast_bp, smart_reorder_bp, imports_bp"
    )
    app_content = app_content.replace(
        "app.register_blueprint(smart_reorder_bp, url_prefix='/api/v1/smart-reorder')",
        "app.register_blueprint(smart_reorder_bp, url_prefix='/api/v1/smart-reorder')\n    app.register_blueprint(imports_bp, url_prefix='/api/v1/imports')"
    )
    with open(app_init, "w") as f:
        f.write(app_content)

print("Updated __init__.py files.")
