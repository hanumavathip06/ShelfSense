import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getApprovals, approveItem, rejectItem } from '../lib/api';
import { toast } from 'react-hot-toast';
import { Skeleton } from '../components/ui/Skeleton';
import { PurchaseOrders } from './PurchaseOrders';
import { Discrepancies } from './Discrepancies';

export function Approvals() {
  const [activeTab, setActiveTab] = useState<'pos' | 'adjustments' | 'discrepancies'>('pos');
  const queryClient = useQueryClient();
  const [reason, setReason] = useState('');
  const [activeItem, setActiveItem] = useState<{type: string, id: number} | null>(null);
  
  const { data: approvals, isLoading } = useQuery({
    queryKey: ['approvals'],
    queryFn: getApprovals
  });

  const approveMutation = useMutation({
    mutationFn: approveItem,
    onSuccess: () => {
      toast.success('Approved successfully');
      setReason('');
      setActiveItem(null);
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.error || 'Failed to approve');
    }
  });

  const rejectMutation = useMutation({
    mutationFn: rejectItem,
    onSuccess: () => {
      toast.success('Rejected successfully');
      setReason('');
      setActiveItem(null);
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.error || 'Failed to reject');
    }
  });

  const handleAction = (action: 'approve' | 'reject') => {
    if (!reason.trim()) {
      toast.error('A mandatory reason is required for this action');
      return;
    }
    if (activeItem) {
      if (action === 'approve') {
        approveMutation.mutate({ type: activeItem.type, id: activeItem.id, reason });
      } else {
        rejectMutation.mutate({ type: activeItem.type, id: activeItem.id, reason });
      }
    }
  };

  if (isLoading) {
    return <div className="p-6"><Skeleton className="h-64" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-serif text-primary">Approvals Desk</h1>
        <div className="flex bg-surface border border-border p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('pos')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'pos' ? 'bg-primary text-surface' : 'text-secondary hover:text-primary'}`}
          >
            Purchase Orders
          </button>
          <button
            onClick={() => setActiveTab('adjustments')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'adjustments' ? 'bg-primary text-surface' : 'text-secondary hover:text-primary'}`}
          >
            Stock Adjustments
          </button>
          <button
            onClick={() => setActiveTab('discrepancies')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'discrepancies' ? 'bg-primary text-surface' : 'text-secondary hover:text-primary'}`}
          >
            Discrepancies
          </button>
        </div>
      </div>

      {activeTab === 'pos' && (
        <div className="space-y-6">
          {approvals?.purchase_orders?.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-accent">Pending Your Approval</h2>
              {approvals.purchase_orders.map((po: any) => (
                <Card key={`po-${po.id}`} className="border-accent/30 shadow-md">
                  <CardHeader className="bg-accent/5">
                    <CardTitle className="flex justify-between items-center text-accent">
                      <span>Purchase Order #{po.id}</span>
                      <span className="text-sm font-normal text-secondary">Created by {po.created_by}</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-4">
                    <div className="flex justify-between text-sm">
                      <div><span className="font-semibold">Supplier:</span> {po.supplier}</div>
                      <div><span className="font-semibold">Total:</span> ${po.total_amount?.toFixed(2)}</div>
                    </div>
                    
                    <div className="border border-border rounded-md overflow-hidden">
                      <table className="w-full text-sm text-left">
                        <thead className="bg-surface text-secondary">
                          <tr>
                            <th className="p-2 font-semibold border-b border-border">Product ID</th>
                            <th className="p-2 font-semibold border-b border-border">Requested Qty</th>
                            <th className="p-2 font-semibold border-b border-border bg-accent/5">Forecast</th>
                            <th className="p-2 font-semibold border-b border-border bg-accent/5">Safety Stock</th>
                            <th className="p-2 font-semibold border-b border-border bg-accent/5">On Hand</th>
                          </tr>
                        </thead>
                        <tbody>
                          {po.items.map((item: any, idx: number) => (
                            <tr key={idx} className="border-b border-border last:border-0 hover:bg-surface/50">
                              <td className="p-2 font-mono">{item.product_id}</td>
                              <td className="p-2">{item.quantity}</td>
                              <td className="p-2 bg-accent/5">{item.forecast_qty || '-'}</td>
                              <td className="p-2 bg-accent/5">{item.safety_stock || '-'}</td>
                              <td className="p-2 bg-accent/5">{item.on_hand || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {activeItem?.id === po.id && activeItem?.type === 'po' ? (
                      <div className="pt-4 border-t border-border space-y-3">
                        <textarea 
                          className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none"
                          placeholder="Mandatory reason for approval/rejection..."
                          value={reason}
                          onChange={(e) => setReason(e.target.value)}
                          rows={2}
                        />
                        <div className="flex gap-2">
                          <Button variant="success" onClick={() => handleAction('approve')} disabled={approveMutation.isPending || rejectMutation.isPending}>Confirm Approve</Button>
                          <Button variant="danger" onClick={() => handleAction('reject')} disabled={approveMutation.isPending || rejectMutation.isPending}>Confirm Reject</Button>
                          <Button variant="outline" onClick={() => setActiveItem(null)}>Cancel</Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-end mt-4">
                        <Button variant="primary" onClick={() => { setActiveItem({ type: 'po', id: po.id }); setReason(''); }}>Review & Decision</Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
          <PurchaseOrders />
        </div>
      )}

      {activeTab === 'adjustments' && (
        <div className="space-y-6">
          {!approvals?.stock_adjustments?.length ? (
            <Card>
              <CardContent className="py-12 text-center text-secondary">
                <p>No stock adjustments pending approval.</p>
              </CardContent>
            </Card>
          ) : (
            approvals.stock_adjustments.map((adj: any) => (
              <Card key={`adj-${adj.id}`}>
                <CardHeader>
                  <CardTitle className="text-lg">Stock Adjustment #{adj.id}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm bg-surface p-4 rounded-md">
                    <div><span className="text-secondary block text-xs uppercase">Product ID</span> <span className="font-semibold font-mono">{adj.product_id}</span></div>
                    <div><span className="text-secondary block text-xs uppercase">Requested Change</span> <span className={`font-semibold ${adj.change_qty > 0 ? 'text-success' : 'text-danger'}`}>{adj.change_qty > 0 ? '+' : ''}{adj.change_qty}</span></div>
                    <div><span className="text-secondary block text-xs uppercase">Reason</span> <span className="capitalize">{adj.reason.replace('_', ' ')}</span></div>
                    <div><span className="text-secondary block text-xs uppercase">Requested By (User ID)</span> {adj.performed_by}</div>
                  </div>

                  {activeItem?.id === adj.id && activeItem?.type === 'adjustment' ? (
                    <div className="pt-4 border-t border-border space-y-3">
                      <textarea 
                        className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none"
                        placeholder="Mandatory reason for approval/rejection..."
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        rows={2}
                      />
                      <div className="flex gap-2">
                        <Button variant="success" onClick={() => handleAction('approve')} disabled={approveMutation.isPending || rejectMutation.isPending}>Confirm Approve</Button>
                        <Button variant="danger" onClick={() => handleAction('reject')} disabled={approveMutation.isPending || rejectMutation.isPending}>Confirm Reject</Button>
                        <Button variant="outline" onClick={() => setActiveItem(null)}>Cancel</Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex justify-end mt-4">
                      <Button variant="primary" onClick={() => { setActiveItem({ type: 'adjustment', id: adj.id }); setReason(''); }}>Review & Decision</Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {activeTab === 'discrepancies' && <Discrepancies />}
    </div>
  );
}
