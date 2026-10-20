import { useQuery } from '@tanstack/react-query';
import { getRolesPermissions } from '../lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';

export function RolesPermissions() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-roles-permissions'],
    queryFn: getRolesPermissions
  });

  if (isLoading) return <div className="p-6"><Skeleton className="h-64" /></div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(data || {}).map(([role, perms]: [string, any]) => (
          <Card key={role}>
            <CardHeader>
              <CardTitle className="capitalize">{role}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {perms.sort().map((p: string) => (
                  <div key={p} className="text-xs bg-surface border border-border p-2 rounded">
                    {p}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
