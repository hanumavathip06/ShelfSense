import os
import re

app_tsx_path = "d:/Shashi/ShelfSense/frontend/src/App.tsx"
sidebar_path = "d:/Shashi/ShelfSense/frontend/src/components/layout/Sidebar.tsx"

# 1. Update App.tsx
with open(app_tsx_path, "r", encoding="utf-8") as f:
    app_content = f.read()

if "ImportData" not in app_content:
    app_content = app_content.replace(
        "import { Classification } from './pages/Classification';",
        "import { Classification } from './pages/Classification';\nimport { ImportData } from './pages/ImportData';"
    )
    app_content = app_content.replace(
        '<Route path="reports" element={<Reports />} />',
        '<Route path="reports" element={<Reports />} />\n          <Route path="import" element={<ImportData />} />'
    )
    with open(app_tsx_path, "w", encoding="utf-8") as f:
        f.write(app_content)

# 2. Update Sidebar.tsx
with open(sidebar_path, "r", encoding="utf-8") as f:
    sidebar_content = f.read()

if "ImportData" not in sidebar_content and "Bulk Import" not in sidebar_content:
    sidebar_content = sidebar_content.replace(
        "import { LayoutDashboard, Package, AlertTriangle, BarChart3, Users, Brain, Zap, Grid3X3 } from 'lucide-react';",
        "import { LayoutDashboard, Package, AlertTriangle, BarChart3, Users, Brain, Zap, Grid3X3, UploadCloud } from 'lucide-react';"
    )
    
    sidebar_content = sidebar_content.replace(
        "{ name: 'Reports', href: '/reports', icon: BarChart3 },",
        "{ name: 'Reports', href: '/reports', icon: BarChart3 },\n  { name: 'Bulk Import', href: '/import', icon: UploadCloud },"
    )
    
    with open(sidebar_path, "w", encoding="utf-8") as f:
        f.write(sidebar_content)

print("Updated Frontend Routing & Navigation")
