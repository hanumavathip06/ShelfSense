import os

pages_dir = "d:/Shashi/ShelfSense/frontend/src/pages"
dashboards_dir = os.path.join(pages_dir, "dashboards")
os.makedirs(dashboards_dir, exist_ok=True)

staff_dashboard_content = """import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Package, PlusCircle, AlertCircle, Scan, ClipboardList, Activity } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api';
import { Skeleton } from '../../components/ui/Skeleton';
import { DataTable } from '../../components/ui/DataTable';

export function StaffDashboard() {
  const { data: movements, isLoading } = useQuery({
    queryKey: ['my-movements'],
    queryFn: async () => {
      const res = await api.get('/analytics/movements/trends?days=7');
      return res.data; // Just a placeholder for staff movements
    }
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-serif text-primary">Warehouse Operations</h1>
      
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center gap-2">
              <Scan className="h-6 w-6" />
              <span>Scan SKU</span>
            </Button>
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center gap-2">
              <PlusCircle className="h-6 w-6" />
              <span>Receive Stock</span>
            </Button>
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center gap-2">
              <Package className="h-6 w-6" />
              <span>Record Movement</span>
            </Button>
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center gap-2 border-danger text-danger hover:bg-danger/10">
              <AlertCircle className="h-6 w-6" />
              <span>Report Damage</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* My Tasks */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5 text-accent" />
              My Tasks Today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-surface border border-border rounded-lg">
                <div>
                  <p className="text-sm font-bold text-primary">Pick Order #1024</p>
                  <p className="text-xs text-secondary">Aisle 4, Shelf B</p>
                </div>
                <Button variant="primary" size="sm">Start</Button>
              </div>
              <div className="flex items-center justify-between p-3 bg-surface border border-border rounded-lg">
                <div>
                  <p className="text-sm font-bold text-primary">Cycle Count</p>
                  <p className="text-xs text-secondary">Electronics Section</p>
                </div>
                <Button variant="primary" size="sm">Start</Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-success" />
              My Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="text-sm text-secondary p-4 bg-background rounded-lg border border-border text-center">
                Activity feed initialized. (Mock data).
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
"""

manager_dashboard_content = """import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { StatTile } from '../../components/ui/StatTile';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { IndianRupee, AlertTriangle, CheckCircle, TrendingUp, Users } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getSummary } from '../../lib/api';
import { Skeleton } from '../../components/ui/Skeleton';

export function ManagerDashboard() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['manager-summary'],
    queryFn: getSummary,
  });

  if (isLoading) return <div className="space-y-6"><Skeleton className="h-32 w-full rounded-xl" /></div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-serif text-primary">Store Oversight</h1>
      
      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatTile title="Stock Value" value={`₹${summary?.inventory_value?.toFixed(2) || '0.00'}`} icon={IndianRupee} color="text-success" />
        <StatTile title="Low Stock Items" value={summary?.low_stock_count || 0} icon={AlertTriangle} color="text-warning" />
        <StatTile title="Pending Approvals" value="4" icon={CheckCircle} color="text-accent" />
        <StatTile title="Turnover Rate" value="1.2x" icon={TrendingUp} color="text-primary" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Approvals Queue */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Approval Queue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-surface border border-border rounded-lg flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-primary">PO-2023</span>
                    <Badge variant="warning">Pending</Badge>
                  </div>
                  <p className="text-xs text-secondary mt-1">Supplier: TechCorp - ₹45,000</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" className="text-danger border-danger hover:bg-danger/10 text-xs py-1">Reject</Button>
                  <Button variant="primary" className="text-xs py-1">Approve</Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Activity Feed */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Team Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-xs text-secondary flex flex-col gap-1 pb-3 border-b border-border">
                <span className="font-bold text-primary">Staff User</span>
                <span>Received 50x ELC-001</span>
                <span className="text-muted">10 mins ago</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
"""

dashboard_router_content = """import React from 'react';
import { useAuth } from '../context/AuthContext';
import { AdminDashboard } from './dashboards/AdminDashboard';
import { ManagerDashboard } from './dashboards/ManagerDashboard';
import { StaffDashboard } from './dashboards/StaffDashboard';

export function Dashboard() {
  const { user } = useAuth();
  
  if (!user) return null;
  
  if (user.role === 'admin') return <AdminDashboard />;
  if (user.role === 'manager') return <ManagerDashboard />;
  return <StaffDashboard />;
}
"""

# Rename existing Dashboard to AdminDashboard
admin_dashboard_path = os.path.join(dashboards_dir, "AdminDashboard.tsx")
old_dashboard_path = os.path.join(pages_dir, "Dashboard.tsx")

if os.path.exists(old_dashboard_path):
    with open(old_dashboard_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("export function Dashboard()", "export function AdminDashboard()")
    with open(admin_dashboard_path, "w", encoding="utf-8") as f:
        f.write(content)

with open(os.path.join(dashboards_dir, "StaffDashboard.tsx"), "w", encoding="utf-8") as f:
    f.write(staff_dashboard_content)
    
with open(os.path.join(dashboards_dir, "ManagerDashboard.tsx"), "w", encoding="utf-8") as f:
    f.write(manager_dashboard_content)

with open(old_dashboard_path, "w", encoding="utf-8") as f:
    f.write(dashboard_router_content)

print("Dashboards created successfully.")
