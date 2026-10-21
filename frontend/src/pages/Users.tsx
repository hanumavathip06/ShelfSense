import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getUsers, updateUser, revokeUserSessions } from '../lib/api';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { DataTable } from '../components/ui/DataTable';
import { RolesPermissions } from './RolesPermissions';
import { Security } from './Security';

export function Users() {
  const [activeTab, setActiveTab] = useState<'users' | 'roles' | 'security'>('users');
  const queryClient = useQueryClient();

  const { data: usersData, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => getUsers({ limit: 100 }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('User updated successfully');
    },
    onError: (err: any) => toast.error(err.response?.data?.error?.message || 'Failed to update user'),
  });

  const revokeMutation = useMutation({
    mutationFn: (id: number) => revokeUserSessions(id),
    onSuccess: () => toast.success('Sessions revoked'),
    onError: () => toast.error('Failed to revoke sessions'),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-serif text-primary">User Management</h1>
        <div className="flex bg-surface border border-border p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'users' ? 'bg-primary text-surface' : 'text-secondary hover:text-primary'}`}
          >
            Users
          </button>
          <button
            onClick={() => setActiveTab('roles')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'roles' ? 'bg-primary text-surface' : 'text-secondary hover:text-primary'}`}
          >
            Roles & Permissions
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'security' ? 'bg-primary text-surface' : 'text-secondary hover:text-primary'}`}
          >
            Security
          </button>
        </div>
      </div>
      
      {activeTab === 'users' && (
        <div className="w-full">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full rounded-xl" />)}
            </div>
          ) : usersData?.items?.length === 0 ? (
            <EmptyState title="No users found" />
          ) : (
            <DataTable headers={['Name', 'Email', 'Role', 'Status', 'Actions']}>
              {usersData?.items?.map((user: any) => (
                <tr key={user.id} className="hover:bg-background/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary">
                    {user.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-secondary">
                    {user.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary">
                    <select
                      value={user.role}
                      onChange={(e) => updateMutation.mutate({ id: user.id, data: { role: e.target.value } })}
                      disabled={updateMutation.isPending}
                      className="px-3 py-1.5 rounded-md border border-border bg-surface text-primary focus:outline-none focus:ring-2 focus:ring-accent font-sans text-xs uppercase tracking-widest font-bold shadow-sm"
                    >
                      <option value="admin">Admin</option>
                      <option value="manager">Manager</option>
                      <option value="staff">Staff</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary">
                    <button
                      onClick={() => updateMutation.mutate({ id: user.id, data: { is_active: !user.is_active } })}
                      className={`px-2 py-1 rounded text-xs font-bold ${user.is_active ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'}`}
                    >
                      {user.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary space-x-2">
                    <button 
                      onClick={() => updateMutation.mutate({ id: user.id, data: { needs_password_reset: true } })}
                      className="text-accent hover:underline text-xs"
                    >
                      Force PW Reset
                    </button>
                    <button 
                      onClick={() => revokeMutation.mutate(user.id)}
                      className="text-danger hover:underline text-xs"
                    >
                      Revoke Sessions
                    </button>
                  </td>
                </tr>
              ))}
            </DataTable>
          )}
        </div>
      )}

      {activeTab === 'roles' && <RolesPermissions />}
      {activeTab === 'security' && <Security />}
    </div>
  );
}
