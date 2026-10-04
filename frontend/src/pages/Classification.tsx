import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { Grid3X3 } from 'lucide-react';
import { getAbcXyzClassification } from '../lib/api';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';

const ABC_COLORS: Record<string, string> = { A: '#4338CA', B: '#059669', C: '#D97706' };
const XYZ_COLORS: Record<string, string> = { X: '#10B981', Y: '#F59E0B', Z: '#EF4444' };

const MATRIX_COLORS: Record<string, string> = {
  AX: '#312E81', AY: '#4338CA', AZ: '#6366F1',
  BX: '#065F46', BY: '#059669', BZ: '#34D399',
  CX: '#92400E', CY: '#D97706', CZ: '#FCD34D',
};

export function Classification() {
  const { data, isLoading } = useQuery({
    queryKey: ['abc-xyz'],
    queryFn: getAbcXyzClassification,
  });

  const classification = data?.classification || [];
  const summary = data?.summary || {};

  // Prepare ABC pie chart data
  const abcPieData = summary.abc_distribution
    ? Object.entries(summary.abc_distribution).map(([cls, count]) => ({
        name: `Class ${cls}`,
        value: count as number,
        pct: summary.abc_value_percentages?.[cls] || 0
      }))
    : [];

  // Prepare XYZ pie chart data
  const xyzPieData = summary.xyz_distribution
    ? Object.entries(summary.xyz_distribution).map(([cls, count]) => ({
        name: `Class ${cls}`,
        value: count as number,
      }))
    : [];

  // Prepare matrix distribution bar chart data
  const matrixData = summary.matrix
    ? Object.entries(summary.matrix).map(([cls, count]) => ({
        name: cls,
        count: count as number,
      })).sort((a, b) => a.name.localeCompare(b.name))
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-success/10 rounded-lg">
          <Grid3X3 className="h-6 w-6 text-success" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-primary">ABC-XYZ Classification</h1>
          <p className="text-sm text-secondary">Inventory segmentation by value (ABC) and demand variability (XYZ)</p>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {[1, 2, 3].map(i => <Skeleton key={i} className="h-48 w-full" />)}
          </div>
          <Skeleton className="h-96 w-full" />
        </div>
      ) : classification.length === 0 ? (
        <EmptyState title="No classification data" description="Add products and stock movements to generate ABC-XYZ classification." />
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-lg bg-surface border border-border shadow-sm p-5">
              <p className="text-sm text-secondary">Total Products</p>
              <p className="text-3xl font-bold text-primary mt-1">{summary.total_products}</p>
            </div>
            <div className="rounded-lg bg-surface border border-border shadow-sm p-5">
              <p className="text-sm text-secondary">Total Inventory Value</p>
              <p className="text-3xl font-bold text-primary mt-1">₹{summary.total_inventory_value?.toLocaleString()}</p>
            </div>
            <div className="rounded-lg bg-surface border border-border shadow-sm p-5">
              <p className="text-sm text-secondary">Class A Value Share</p>
              <p className="text-3xl font-bold text-accent mt-1">{summary.abc_value_percentages?.A || 0}%</p>
            </div>
            <div className="rounded-lg bg-surface border border-border shadow-sm p-5">
              <p className="text-sm text-secondary">High Variability (Z)</p>
              <p className="text-3xl font-bold text-danger mt-1">{summary.xyz_distribution?.Z || 0}</p>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* ABC Pie Chart */}
            <div className="rounded-lg bg-surface border border-border shadow-sm p-6">
              <h3 className="text-lg font-medium text-primary mb-4">ABC Distribution</h3>
              <div className="h-64">
                {abcPieData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={abcPieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}`}
                      >
                        {abcPieData.map((entry, idx) => (
                          <Cell key={idx} fill={ABC_COLORS[entry.name.split(' ')[1]] || '#6B7280'} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : <EmptyState title="No data" />}
              </div>
            </div>

            {/* XYZ Pie Chart */}
            <div className="rounded-lg bg-surface border border-border shadow-sm p-6">
              <h3 className="text-lg font-medium text-primary mb-4">XYZ Distribution</h3>
              <div className="h-64">
                {xyzPieData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={xyzPieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}`}
                      >
                        {xyzPieData.map((entry, idx) => (
                          <Cell key={idx} fill={XYZ_COLORS[entry.name.split(' ')[1]] || '#6B7280'} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : <EmptyState title="No data" />}
              </div>
            </div>

            {/* Combined Matrix Bar Chart */}
            <div className="rounded-lg bg-surface border border-border shadow-sm p-6">
              <h3 className="text-lg font-medium text-primary mb-4">Matrix Distribution</h3>
              <div className="h-64">
                {matrixData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={matrixData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                      <XAxis dataKey="name" tick={{ fill: '#6B7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: '#6B7280' }} axisLine={false} tickLine={false} allowDecimals={false} />
                      <RechartsTooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }} />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {matrixData.map((entry, idx) => (
                          <Cell key={idx} fill={MATRIX_COLORS[entry.name] || '#6B7280'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : <EmptyState title="No data" />}
              </div>
            </div>
          </div>

          {/* 3x3 Matrix Grid */}
          <div className="rounded-lg bg-surface border border-border shadow-sm p-6">
            <h3 className="text-lg font-medium text-primary mb-4">ABC-XYZ Strategy Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="p-3 border border-border bg-background text-sm font-medium text-secondary"></th>
                    <th className="p-3 border border-border bg-background text-sm font-medium text-center text-success">X (Stable)</th>
                    <th className="p-3 border border-border bg-background text-sm font-medium text-center text-warning">Y (Variable)</th>
                    <th className="p-3 border border-border bg-background text-sm font-medium text-center text-danger">Z (Erratic)</th>
                  </tr>
                </thead>
                <tbody>
                  {['A', 'B', 'C'].map(abc => (
                    <tr key={abc}>
                      <td className="p-3 border border-border bg-background text-sm font-medium text-center" style={{ color: ABC_COLORS[abc] }}>
                        {abc} ({abc === 'A' ? 'High Value' : abc === 'B' ? 'Medium Value' : 'Low Value'})
                      </td>
                      {['X', 'Y', 'Z'].map(xyz => {
                        const cls = `${abc}${xyz}`;
                        const items = classification.filter((c: any) => c.combined_class === cls);
                        const strategy = items[0]?.strategy;
                        return (
                          <td key={cls} className="p-3 border border-border text-xs" style={{ backgroundColor: `${MATRIX_COLORS[cls]}08` }}>
                            <div className="font-semibold text-primary mb-1">{cls} ({items.length} items)</div>
                            {strategy && (
                              <>
                                <div className="text-secondary"><strong>Monitor:</strong> {strategy.monitoring_level}</div>
                                <div className="text-secondary mt-0.5"><strong>Forecast:</strong> {strategy.forecasting_approach}</div>
                              </>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Product Classification Table */}
          <div className="rounded-lg bg-surface border border-border shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-border bg-background">
              <h3 className="text-lg font-medium text-primary">Product Classification Details</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-border">
                <thead className="bg-surface">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Product</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-secondary uppercase tracking-wider">ABC</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-secondary uppercase tracking-wider">XYZ</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-secondary uppercase tracking-wider">Combined</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Value</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">CV</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Priority</th>
                  </tr>
                </thead>
                <tbody className="bg-surface divide-y divide-border">
                  {classification.map((item: any) => (
                    <tr key={item.product_id}>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="text-sm font-medium text-primary">{item.product_name}</div>
                        <div className="text-xs text-secondary">{item.sku}</div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-center">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold" style={{ color: ABC_COLORS[item.abc_class] }}>
                          {item.abc_class}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-center">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold" style={{ color: XYZ_COLORS[item.xyz_class] }}>
                          {item.xyz_class}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-center">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold text-white" style={{ backgroundColor: MATRIX_COLORS[item.combined_class] || '#6B7280' }}>
                          {item.combined_class}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-secondary text-right">
                        ₹{item.total_value?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-secondary text-right">
                        {item.coefficient_of_variation?.toFixed(3)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-xs text-secondary">
                        {item.strategy?.priority}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
