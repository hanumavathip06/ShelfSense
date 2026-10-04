import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Download } from 'lucide-react';
import Papa from 'papaparse';
import { getTrends, getProducts, getCategories, getCategoryStock } from '../lib/api';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';

export function Reports() {
  const { data: trendsData, isLoading: loadingTrends } = useQuery({
    queryKey: ['trends'],
    queryFn: () => getTrends(30),
  });

  const { data: productsData, isLoading: loadingProducts } = useQuery({
    queryKey: ['products-all'],
    queryFn: () => getProducts({ limit: 100 }),
  });

  const { data: categoriesData, isLoading: loadingCategories } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  const { data: categoryChartData = [], isLoading: loadingCategoryStock } = useQuery<{ name: string; stock: number }[]>({
    queryKey: ['category-stock'],
    queryFn: getCategoryStock,
  });

  const loading = loadingTrends || loadingProducts || loadingCategories || loadingCategoryStock;

  // Prepare line chart data
  const trendChartData = trendsData
    ? Object.entries(trendsData).map(([date, amount]) => ({
        date,
        movements: amount,
      })).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    : [];

  const exportCSV = () => {
    if (!productsData?.items) return;
    
    const exportData = productsData.items.map((p: any) => ({
      ID: p.id,
      Name: p.name,
      SKU: p.sku,
      Category: categoriesData?.items?.find((c: any) => c.id === p.category_id)?.name || 'Unknown',
      Quantity: p.quantity,
      Threshold: p.reorder_threshold,
      Price: p.unit_price,
      Supplier: p.supplier || 'N/A'
    }));

    const csv = Papa.unparse(exportData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', 'inventory_report.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold text-primary">Reports & Analytics</h1>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Skeleton className="h-96 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-primary">Reports & Analytics</h1>
        <button
          onClick={exportCSV}
          className="inline-flex items-center justify-center rounded-md bg-surface border border-border px-4 py-2 text-sm font-medium text-primary hover:bg-background shadow-sm"
        >
          <Download className="mr-2 h-4 w-4 text-secondary" />
          Export CSV
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg bg-surface border border-border shadow-sm p-6">
          <h3 className="text-lg font-medium text-primary mb-4">Stock Levels by Category</h3>
          <div className="h-80">
            {categoryChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                  <XAxis dataKey="name" tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} />
                  <YAxis tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} />
                  <RechartsTooltip cursor={{fill: '#F8F9FB'}} contentStyle={{borderRadius: '8px', border: '1px solid #E5E7EB'}} />
                  <Bar dataKey="stock" fill="#4338CA" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState title="No data" />
            )}
          </div>
        </div>

        <div className="rounded-lg bg-surface border border-border shadow-sm p-6">
          <h3 className="text-lg font-medium text-primary mb-4">Movement Trends (Last 30 Days)</h3>
          <div className="h-80">
            {trendChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendChartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                  <XAxis dataKey="date" tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} />
                  <YAxis tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} />
                  <RechartsTooltip contentStyle={{borderRadius: '8px', border: '1px solid #E5E7EB'}} />
                  <Line type="monotone" dataKey="movements" stroke="#4338CA" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState title="No movements" />
            )}
          </div>
        </div>
      </div>

      <div className="rounded-lg bg-surface border border-border shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-border bg-background">
          <h3 className="text-lg font-medium text-primary">Product Breakdown</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-surface">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Product</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Category</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Qty</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Value</th>
              </tr>
            </thead>
            <tbody className="bg-surface divide-y divide-border">
              {productsData?.items?.map((product: any) => (
                <tr key={product.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary">{product.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary">
                    {categoriesData?.items?.find((c: any) => c.id === product.category_id)?.name || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary text-right">{product.quantity}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary text-right">
                    ₹{(product.quantity * product.unit_price).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
