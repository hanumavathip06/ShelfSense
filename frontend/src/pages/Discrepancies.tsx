import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getDiscrepancies, acceptDiscrepancy, dismissDiscrepancy } from '../lib/api';
import { toast } from 'react-hot-toast';
import { Skeleton } from '../components/ui/Skeleton';

export function Discrepancies() {
  const queryClient = useQueryClient();
  const [reason, setReason] = useState('');
  const [activeItem, setActiveItem] = useState<number | null>(null);
  const [changeQty, setChangeQty] = useState(0);

  const { data: discrepancies, isLoading } = useQuery({
    queryKey: ['discrepancies'],
    queryFn: getDiscrepancies
  });

  const acceptMutation = useMutation({
    mutationFn: ({ id, change_qty }: { id: number, change_qty: number }) => acceptDiscrepancy(id, { change_qty }),
    onSuccess: () => {
      toast.success('Discrepancy accepted. A pending stock adjustment was created.');
      setActiveItem(null);
      queryClient.invalidateQueries({ queryKey: ['discrepancies'] });
    },
    onError: () => toast.error('Failed to accept discrepancy')
  });

  const dismissMutation = useMutation({
    mutationFn: ({ id, reason }: { id: number, reason: string }) => dismissDiscrepancy(id, reason),
    onSuccess: () => {
      toast.success('Discrepancy dismissed.');
      setReason('');
      setActiveItem(null);
      queryClient.invalidateQueries({ queryKey: ['discrepancies'] });
    },
    onError: () => toast.error('Failed to dismiss discrepancy')
  });

  if (isLoading) return <div className="p-6"><Skeleton className="h-64" /></div>;

  return (
    <div className="space-y-6">

      {!discrepancies || discrepancies.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-secondary">
            <p>No open discrepancies to review.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {discrepancies.map((issue: any) => (
            <Card key={issue.id} className="border-accent/30">
              <CardHeader className="bg-accent/5">
                <CardTitle className="flex justify-between items-center text-accent">
                  <span className="capitalize">{issue.type.replace(/_/g, ' ')}</span>
                  <span className="text-sm font-normal text-secondary">{new Date(issue.created_at).toLocaleDateString()}</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                <div className="text-sm">
                  <p><span className="font-semibold">Product ID:</span> {issue.product_id || 'N/A'}</p>
                  <p><span className="font-semibold">Reported by User:</span> {issue.user_id}</p>
                  <p className="mt-2 bg-surface p-2 rounded border border-border">{issue.notes}</p>
                </div>

                {activeItem === issue.id ? (
                  <div className="pt-4 border-t border-border space-y-3">
                    <p className="font-medium text-sm text-secondary">Resolution Decision</p>
                    <div className="grid grid-cols-2 gap-4 border border-border rounded p-4">
                      <div className="space-y-2">
                        <label className="text-sm font-bold text-success block">Accept (Adjust Stock)</label>
                        <input 
                          type="number" 
                          placeholder="Stock Adjustment Qty (e.g. -5)" 
                          className="w-full bg-surface border border-border rounded-md px-3 py-2 text-sm text-primary outline-none"
                          value={changeQty}
                          onChange={(e) => setChangeQty(parseInt(e.target.value))}
                        />
                        <Button 
                          variant="success" 
                          className="w-full"
                          onClick={() => acceptMutation.mutate({ id: issue.id, change_qty: changeQty })}
                          disabled={acceptMutation.isPending}
                        >
                          Accept & Adjust
                        </Button>
                      </div>
                      
                      <div className="space-y-2">
                        <label className="text-sm font-bold text-danger block">Dismiss (Ignore)</label>
                        <input 
                          type="text" 
                          placeholder="Reason for dismissal" 
                          className="w-full bg-surface border border-border rounded-md px-3 py-2 text-sm text-primary outline-none"
                          value={reason}
                          onChange={(e) => setReason(e.target.value)}
                        />
                        <Button 
                          variant="danger" 
                          className="w-full"
                          onClick={() => {
                            if (!reason) { toast.error('Reason required'); return; }
                            dismissMutation.mutate({ id: issue.id, reason });
                          }}
                          disabled={dismissMutation.isPending}
                        >
                          Dismiss
                        </Button>
                      </div>
                    </div>
                    <Button variant="outline" onClick={() => setActiveItem(null)}>Cancel</Button>
                  </div>
                ) : (
                  <div className="flex justify-end mt-4">
                    <Button variant="primary" onClick={() => { setActiveItem(issue.id); setReason(''); setChangeQty(0); }}>Review</Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
