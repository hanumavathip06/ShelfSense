import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Package, IndianRupee, AlertTriangle, Bell, Brain, ShieldAlert } from 'lucide-react';
import { Link } from 'react-router-dom';
import { getSummary, getTrends, getCategoryStock, getAnomalies } from '../../lib/api';
import { Skeleton } from '../../components/ui/Skeleton';
import { EmptyState } from '../../components/ui/EmptyState';
import { StatTile } from '../../components/ui/StatTile';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#EF4444',
  HIGH: '#F59E0B',
  MEDIUM: '#6366F1',
  LOW: '#6B7280',
};

export function AdminDashboard() {
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ['summary'],
    queryFn: getSummary,
  });

  const { data: trendsData, isLoading: loadingTrends } = useQuery({
    queryKey: ['trends'],
    queryFn: () => getTrends(30),
  });

  const { data: categoryChartData = [], isLoading: loadingCategoryStock } = useQuery<{ name: string; stock: number }[]>({
    queryKey: ['category-stock'],
    queryFn: getCategoryStock,
  });

  const { data: anomalyData, isLoading: loadingAnomalies } = useQuery({
    queryKey: ['anomalies-dashboard'],
    queryFn: () => getAnomalies(30),
  });

  const loading = loadingSummary || loadingTrends || loadingCategoryStock;

  // Prepare line chart data
  const trendChartData = trendsData
    ? Object.entries(trendsData).map(([date, amount]) => ({
        date,
        movements: amount,
      })).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    : [];

  const kpis = [
    { name: 'Total SKUs', value: summary?.total_skus || 0, icon: Package, color: 'text-primary' },
    { name: 'Inventory Value', value: `₹${summary?.inventory_value?.toFixed(2) || '0.00'}`, icon: IndianRupee, color: 'text-success' },
    { name: 'Low Stock', value: summary?.low_stock_count || 0, icon: AlertTriangle, color: 'text-danger' },
    { name: 'Unread Notifications', value: summary?.pending_notifications || 0, icon: Bell, color: 'text-warning' },
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-serif text-primary">Dashboard</h1>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-32 w-full rounded-xl" />)}
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Skeleton className="h-96 w-full rounded-xl" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-serif text-primary">Dashboard</h1>
      
      {/* KPIs */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi) => (
          <StatTile key={kpi.name} title={kpi.name} value={kpi.value} icon={kpi.icon} color={kpi.color} />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Stock Levels by Category</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              {categoryChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryChartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis dataKey="name" tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} />
                    <YAxis tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} />
                    <RechartsTooltip cursor={{fill: '#F8F9FB'}} contentStyle={{borderRadius: '8px', border: '1px solid #E5E7EB'}} />
                    <Bar dataKey="stock" fill="#4A3BCA" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState title="No categories found" description="Create categories to see stock levels." />
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Movement Trends (Last 30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              {trendChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendChartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis dataKey="date" tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} />
                    <YAxis tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} />
                    <RechartsTooltip contentStyle={{borderRadius: '8px', border: '1px solid #E5E7EB'}} />
                    <Line type="monotone" dataKey="movements" stroke="#4A3BCA" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState title="No recent movements" description="Stock movements will appear here." />
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Quick Links + Anomaly Alerts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* AI Quick Access */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="h-5 w-5 mr-2 text-accent" />
              AI & Analytics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Link to="/forecast" className="flex flex-col items-center p-4 rounded-lg bg-accent/5 border border-accent/20 hover:bg-accent/10 transition-colors">
                <Brain className="h-8 w-8 text-accent mb-2" />
                <span className="text-sm font-medium text-primary">AI Forecast</span>
                <span className="text-xs text-secondary mt-1">Demand Prediction</span>
              </Link>
              <Link to="/smart-reorder" className="flex flex-col items-center p-4 rounded-lg bg-warning/5 border border-warning/20 hover:bg-warning/10 transition-colors">
                <AlertTriangle className="h-8 w-8 text-warning mb-2" />
                <span className="text-sm font-medium text-primary">Smart Reorder</span>
                <span className="text-xs text-secondary mt-1">Dynamic EOQ</span>
              </Link>
              <Link to="/classification" className="flex flex-col items-center p-4 rounded-lg bg-success/5 border border-success/20 hover:bg-success/10 transition-colors">
                <Package className="h-8 w-8 text-success mb-2" />
                <span className="text-sm font-medium text-primary">ABC-XYZ</span>
                <span className="text-xs text-secondary mt-1">Classification</span>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Anomaly Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <ShieldAlert className="h-5 w-5 mr-2 text-danger" />
              Anomaly Alerts (Last 30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingAnomalies ? (
              <Skeleton className="h-48 w-full" />
            ) : anomalyData?.anomalies?.length > 0 ? (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {anomalyData.anomalies.slice(0, 5).map((anomaly: any, idx: number) => (
                  <div key={idx} className="flex items-start gap-3 p-3 rounded-md bg-background">
                    <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: SEVERITY_COLORS[anomaly.severity] || '#6B7280' }} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-primary truncate">{anomaly.product_name}</p>
                      <p className="text-xs text-secondary truncate">{anomaly.anomaly_type}</p>
                    </div>
                    <span className="text-xs text-secondary flex-shrink-0 font-mono tracking-wider">{anomaly.severity}</span>
                  </div>
                ))}
                {anomalyData.anomalies.length > 5 && (
                  <p className="text-xs text-secondary text-center pt-1">
                    +{anomalyData.anomalies.length - 5} more anomalies detected
                  </p>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-48 text-sm text-secondary">
                No anomalies detected — all stock movements look normal.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
