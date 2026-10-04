import os
import glob

routes_dir = "d:/Shashi/ShelfSense/backend/app/routes"
files = glob.glob(os.path.join(routes_dir, "*.py"))

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "role_required" in content:
        # Replace imports
        content = content.replace("from app.utils.auth import role_required", "from app.utils.auth import requires_permission, Permission")
        
        # Replace the decorators based on args
        # 1. admin only -> MANAGE_USERS (or MANAGE_SETTINGS)
        content = content.replace("@role_required('admin')", "@requires_permission(Permission.MANAGE_USERS)")
        
        # 2. admin, manager -> EDIT_REORDER_POINTS (a proxy for manager actions)
        content = content.replace("@role_required('admin', 'manager')", "@requires_permission(Permission.EDIT_REORDER_POINTS)")
        
        # 3. admin, manager, staff -> VIEW_DASHBOARD (or RECORD_MOVEMENT)
        content = content.replace("@role_required('admin', 'manager', 'staff')", "@requires_permission(Permission.VIEW_DASHBOARD)")
        
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)

print("Replaced decorators in all route files.")
