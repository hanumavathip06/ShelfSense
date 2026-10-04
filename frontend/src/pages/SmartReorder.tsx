import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Zap, ArrowDown, ArrowUp, Minus, PackagePlus } from 'lucide-react';
import { getSmartReorderAll, adjustStock } from '../lib/api';
import { toast } from 'react-hot-toast';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';

const urgencyConfig: Record<string, { bg: string; text: string; border: string }> = {
  CRITICAL: { bg: 'bg-danger/10', text: 'text-danger', border: 'border-danger/30' },
  HIGH: { bg: 'bg-warning/10', text: 'text-warning', border: 'border-warning/30' },
  MEDIUM: { bg: 'bg-accent/10', text: 'text-accent', border: 'border-accent/30' },
  LOW: { bg: 'bg-success/10', text: 'text-success', border: 'border-success/30' },
};

export function SmartReorder() {
  const queryClient = useQueryClient();

  const { data: recommendations, isLoading } = useQuery({
    queryKey: ['smart-reorder'],
    queryFn: getSmartReorderAll,
  });

  const adjustMutation = useMutation({
    mutationFn: adjustStock,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['smart-reorder'] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Restock logged successfully');
    },
    onError: (err: any) => toast.error(err.response?.data?.error?.message || 'Failed to log restock'),
  });

  const handleRestock = (productId: number) => {
    const qty = window.prompt("Enter quantity to restock:", "50");
    if (!qty || isNaN(Number(qty))) return;
    
    adjustMutation.mutate({
      id: productId,
      data: { change_qty: Number(qty), reason: 'restock' }
    });
  };

  // Summary stats
  const criticalCount = recommendations?.filter((r: any) => r.urgency === 'CRITICAL').length || 0;
  const highCount = recommendations?.filter((r: any) => r.urgency === 'HIGH').length || 0;
  const needsReorder = recommendations?.filter((r: any) => r.needs_reorder).length || 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-warning/10 rounded-lg">
          <Zap className="h-6 w-6 text-warning" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-primary">Smart Reorder & Restock Alerts</h1>
          <p className="text-sm text-secondary">Dynamic EOQ-based reorder point optimization and restock actions</p>
        </div>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-lg bg-danger/5 border border-danger/20 p-4">
          <p className="text-sm text-secondary">Critical / High Urgency</p>
          <p className="text-2xl font-bold text-danger mt-1">{criticalCount + highCount}</p>
        </div>
        <div className="rounded-lg bg-warning/5 border border-warning/20 p-4">
          <p className="text-sm text-secondary">Needs Reorder</p>
          <p className="text-2xl font-bold text-warning mt-1">{needsReorder}</p>
        </div>
        <div className="rounded-lg bg-success/5 border border-success/20 p-4">
          <p className="text-sm text-secondary">Total Products Analyzed</p>
          <p className="text-2xl font-bold text-success mt-1">{recommendations?.length || 0}</p>
        </div>
      </div>

      {/* Recommendations Table */}
      <div className="bg-surface border border-border rounded-lg shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-4">
            {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-16 w-full" />)}
          </div>
        ) : !recommendations || recommendations.length === 0 ? (
          <EmptyState title="No recommendations" description="Add products and stock movements to generate reorder recommendations." />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-background">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Product</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Urgency</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Current Qty</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Static Threshold</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Dynamic ROP</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Safety Stock</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">EOQ</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-secondary uppercase tracking-wider">Comparison</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-surface divide-y divide-border">
                {recommendations.map((rec: any) => {
                  const uc = urgencyConfig[rec.urgency] || urgencyConfig.LOW;
                  const diff = rec.comparison?.difference || 0;
                  
                  return (
                    <tr key={rec.product_id} className={rec.needs_reorder ? 'bg-danger/[0.02]' : ''}>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-primary">{rec.product_name}</div>
                        <div className="text-xs text-secondary">{rec.sku}</div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${uc.bg} ${uc.text}`}>
                          {rec.urgency}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right">
                        <span className={rec.needs_reorder ? 'text-danger font-semibold' : 'text-primary'}>
                          {rec.current_quantity}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-secondary text-right">
                        {rec.static_reorder_threshold}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right">
                        <span className="font-semibold text-accent">{rec.dynamic_reorder_point}</span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-secondary text-right">
                        {rec.safety_stock}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-right">
                        {rec.recommended_order_qty > 0 ? (
                          <span className="font-semibold text-success">{rec.eoq}</span>
                        ) : (
                          <span className="text-secondary">—</span>
                        )}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center">
                        {diff > 0 ? (
                          <span className="inline-flex items-center text-xs text-warning">
                            <ArrowUp className="h-3 w-3 mr-1" />+{diff}
                          </span>
                        ) : diff < 0 ? (
                          <span className="inline-flex items-center text-xs text-success">
                            <ArrowDown className="h-3 w-3 mr-1" />{diff}
                          </span>
                        ) : (
                          <span className="inline-flex items-center text-xs text-secondary">
                            <Minus className="h-3 w-3 mr-1" />0
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-right">
                        <button
                          onClick={() => handleRestock(rec.product_id)}
                          disabled={adjustMutation.isPending}
                          className="inline-flex items-center justify-center rounded-md bg-success/10 px-3 py-1 text-sm font-medium text-success hover:bg-success/20 disabled:opacity-50"
                        >
                          <PackagePlus className="mr-2 h-4 w-4" />
                          Log Restock
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="rounded-lg bg-surface border border-border shadow-sm p-4">
        <h4 className="text-sm font-medium text-primary mb-3">How Dynamic Reorder Points Work</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs text-secondary">
          <div><strong>Dynamic ROP</strong> = (Avg Daily Demand × Lead Time) + Safety Stock</div>
          <div><strong>Safety Stock</strong> = Z × σ_demand × √Lead Time</div>
          <div><strong>EOQ</strong> = √(2 × Annual Demand × Order Cost / Holding Cost)</div>
          <div><strong>Static Threshold</strong> = manually set, fixed value</div>
          <div><strong>Comparison</strong> = Dynamic ROP − Static Threshold (+ means dynamic is more conservative)</div>
          <div><strong>Days to Stockout</strong> = Current Qty / Avg Daily Demand</div>
        </div>
      </div>
    </div>
  );
}
