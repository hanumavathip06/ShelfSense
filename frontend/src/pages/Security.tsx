import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { getSecurityStats, unlockUser } from '../lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';

export function Security() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['admin-security'],
    queryFn: getSecurityStats
  });

  const unlockMutation = useMutation({
    mutationFn: (id: number) => unlockUser(id),
    onSuccess: () => {
      toast.success('User unlocked');
      queryClient.invalidateQueries({ queryKey: ['admin-security'] });
    },
    onError: () => toast.error('Failed to unlock user')
  });

  if (isLoading) return <div className="p-6"><Skeleton className="h-64" /></div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Locked Accounts</CardTitle>
          </CardHeader>
          <CardContent>
            {data?.locked.length === 0 ? (
              <p className="text-sm text-secondary">No locked accounts.</p>
            ) : (
              <div className="space-y-3">
                {data?.locked.map((u: any) => (
                  <div key={u.id} className="flex justify-between items-center p-3 border rounded">
                    <div>
                      <p className="font-semibold">{u.name}</p>
                      <p className="text-xs text-secondary">Locked until: {new Date(u.locked_until).toLocaleString()}</p>
                    </div>
                    <button 
                      onClick={() => unlockMutation.mutate(u.id)}
                      className="text-accent text-sm font-semibold hover:underline"
                    >
                      Unlock
                    </button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Failed Logins</CardTitle>
          </CardHeader>
          <CardContent>
            {data?.recent_failed.length === 0 ? (
              <p className="text-sm text-secondary">No recent failed logins.</p>
            ) : (
              <div className="space-y-3">
                {data?.recent_failed.map((u: any) => (
                  <div key={u.id} className="flex justify-between items-center p-3 border rounded">
                    <div>
                      <p className="font-semibold">{u.name}</p>
                      <p className="text-xs text-secondary">{u.attempts} failed attempts</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Users without 2FA Enabled</CardTitle>
          </CardHeader>
          <CardContent>
            {data?.no_2fa.length === 0 ? (
              <p className="text-sm text-secondary">All users have 2FA enabled.</p>
            ) : (
              <div className="space-y-3">
                {data?.no_2fa.map((u: any) => (
                  <div key={u.id} className="p-3 border rounded">
                    <p className="font-semibold">{u.name}</p>
                    <p className="text-xs text-secondary">{u.email}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
