import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useMutation, useQuery } from '@tanstack/react-query';
import { reportIssue, getProducts } from '../lib/api';
import { toast } from 'react-hot-toast';

export function ReportIssue() {
  const [productQuery, setProductQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [type, setType] = useState('damage');
  const [notes, setNotes] = useState('');

  // Search products
  const { data: products } = useQuery({
    queryKey: ['products-search', productQuery],
    queryFn: () => getProducts({ q: productQuery, limit: 5 }),
    enabled: productQuery.length > 2
  });

  const reportMutation = useMutation({
    mutationFn: reportIssue,
    onSuccess: () => {
      toast.success('Issue reported successfully. Sent to manager review.');
      setSelectedProduct(null);
      setNotes('');
    },
    onError: () => {
      toast.error('Failed to report issue');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!notes) {
      toast.error('Please provide details about the issue');
      return;
    }
    
    reportMutation.mutate({
      product_id: selectedProduct?.id, // Optional
      type,
      notes
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-serif text-primary">Report an Issue</h1>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Issue Details</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary mb-1">Issue Type</label>
                <select 
                  className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none"
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                >
                  <option value="damage">Damaged Stock</option>
                  <option value="shortage">Missing / Shortage</option>
                  <option value="wrong_item">Wrong Item Found</option>
                  <option value="safety_hazard">Safety Hazard</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary mb-1">Related Product (Optional)</label>
                {selectedProduct ? (
                  <div className="flex items-center justify-between p-3 bg-accent/10 border border-accent/20 rounded-md">
                    <div>
                      <p className="font-semibold text-primary">{selectedProduct.name}</p>
                      <p className="text-xs text-secondary">SKU: {selectedProduct.sku}</p>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => setSelectedProduct(null)}>Change</Button>
                  </div>
                ) : (
                  <div>
                    <input 
                      type="text" 
                      className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary focus:border-accent outline-none"
                      placeholder="Type at least 3 chars to search..."
                      value={productQuery}
                      onChange={(e) => setProductQuery(e.target.value)}
                    />
                    {products && products.data && products.data.length > 0 && (
                      <div className="mt-2 border border-border rounded-md bg-surface max-h-40 overflow-y-auto">
                        {products.data.map((p: any) => (
                          <div 
                            key={p.id} 
                            className="p-2 hover:bg-background cursor-pointer text-sm"
                            onClick={() => setSelectedProduct(p)}
                          >
                            <span className="font-semibold">{p.sku}</span> - {p.name}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary mb-1">Description / Notes</label>
                <textarea 
                  className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none h-32"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Describe the issue in detail..."
                  required
                />
              </div>
              
              <Button type="submit" variant="danger" className="w-full" disabled={reportMutation.isPending}>
                {reportMutation.isPending ? 'Submitting...' : 'Submit Report'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
