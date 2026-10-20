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
