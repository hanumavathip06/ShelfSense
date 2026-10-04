import { useState } from 'react';
import { Bell, LogOut, Check } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { getNotifications, markNotificationRead } from '../../lib/api';

export function Topbar() {
  const { user, logout } = useAuth();
  const queryClient = useQueryClient();
  const [showNotifications, setShowNotifications] = useState(false);

  const { data: notificationsData } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => getNotifications({ limit: 10 }),
    refetchInterval: 30000,
  });

  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const unreadCount = notificationsData?.items?.filter((n: any) => !n.is_read).length || 0;

  return (
    <div className="flex h-16 items-center justify-between border-b border-border bg-surface px-6 relative">
      <div className="flex items-center">
        {/* Breadcrumbs or page title could go here */}
      </div>
      <div className="flex items-center space-x-4">
        
        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative rounded-full bg-surface p-1 text-secondary hover:text-primary focus:outline-none"
          >
            <span className="sr-only">View notifications</span>
            <Bell className="h-6 w-6" aria-hidden="true" />
            {unreadCount > 0 && (
              <span className="absolute top-0 right-0 block h-4 w-4 text-[10px] text-white text-center rounded-full bg-danger ring-2 ring-surface">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 rounded-md bg-surface shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
              <div className="p-3 border-b border-border flex justify-between items-center bg-background rounded-t-md">
                <span className="font-semibold text-primary">Notifications</span>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {notificationsData?.items?.length === 0 ? (
                  <div className="p-4 text-center text-sm text-secondary">No notifications</div>
                ) : (
                  <div className="divide-y divide-border">
                    {notificationsData?.items?.map((notif: any) => (
                      <div key={notif.id} className={`p-4 text-sm ${notif.is_read ? 'opacity-60' : 'bg-accent/5'}`}>
                        <div className="flex justify-between items-start">
                          <p className="text-primary font-medium">{notif.type === 'low_stock' ? 'Low Stock Alert' : notif.type}</p>
                          {!notif.is_read && (
                            <button 
                              onClick={() => markReadMutation.mutate(notif.id)}
                              className="text-accent hover:bg-accent/10 p-1 rounded"
                              title="Mark as read"
                            >
                              <Check className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                        <p className="text-secondary mt-1">{notif.message}</p>
                        <p className="text-xs text-secondary/70 mt-2">{new Date(notif.created_at).toLocaleString()}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex flex-col text-right">
            <span className="text-sm font-medium text-primary">{user?.name}</span>
            <span className="text-xs text-secondary capitalize">{user?.role}</span>
          </div>
          
          <button
            onClick={logout}
            className="flex items-center text-sm font-medium text-secondary hover:text-primary ml-2"
          >
            <LogOut className="h-5 w-5 mr-1" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
