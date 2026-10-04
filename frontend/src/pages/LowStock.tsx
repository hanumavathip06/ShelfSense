import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { useQuery } from '@tanstack/react-query';
import { getLowStockLocation } from '../lib/api';
import { Skeleton } from '../components/ui/Skeleton';
import { DataTable } from '../components/ui/DataTable';

export function LowStock() {
  const { data: lowStock, isLoading } = useQuery({
    queryKey: ['low-stock'],
    queryFn: getLowStockLocation
  });

  const columns = [
    { header: 'Product ID', accessorKey: 'product_id' },
    { header: 'Current Quantity', accessorKey: 'quantity' },
    { header: 'Reorder Threshold', accessorKey: 'reorder_threshold' },
    {
      header: 'Status',
      cell: (row: any) => (
        <span className="bg-danger/20 text-danger px-2 py-1 rounded text-xs font-semibold uppercase">
          {row.quantity === 0 ? 'Out of Stock' : 'Low Stock'}
        </span>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-serif text-primary">Location Low Stock</h1>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Items Below Threshold</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
            </div>
          ) : !lowStock || lowStock.length === 0 ? (
            <div className="text-center py-10 text-secondary">
              <p>No low stock items found in your location!</p>
            </div>
          ) : (
            <DataTable columns={columns} data={lowStock} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
