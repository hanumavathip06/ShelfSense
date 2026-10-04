import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Package, PlusCircle, AlertCircle, Scan, ClipboardList, Activity } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMyTasks, getMyActivity, updateTaskStatus } from '../../lib/api';
import { Skeleton } from '../../components/ui/Skeleton';
import { Link } from 'react-router-dom';

export function StaffDashboard() {
  const queryClient = useQueryClient();
  
  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['my-tasks'],
    queryFn: getMyTasks
  });

  const { data: activity, isLoading: activityLoading } = useQuery({
    queryKey: ['my-activity'],
    queryFn: getMyActivity
  });

  const updateStatus = useMutation({
    mutationFn: ({ taskId, status }: { taskId: number, status: string }) => updateTaskStatus(taskId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-tasks'] });
    }
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-serif text-primary">Warehouse Operations</h1>
      
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link to="/inventory">
              <Button variant="outline" className="w-full h-24 flex flex-col items-center justify-center gap-2">
                <Scan className="h-6 w-6" />
                <span>Scan SKU / Cycle Count</span>
              </Button>
            </Link>
            <Button variant="outline" className="h-24 flex flex-col items-center justify-center gap-2 opacity-50 cursor-not-allowed" title="Feature flagged for Phase 6">
              <PlusCircle className="h-6 w-6" />
              <span>Receive Stock</span>
            </Button>
            <Link to="/movements">
              <Button variant="outline" className="w-full h-24 flex flex-col items-center justify-center gap-2">
                <Package className="h-6 w-6" />
                <span>Record Movement</span>
              </Button>
            </Link>
            <Link to="/report-issue">
              <Button variant="outline" className="w-full h-24 flex flex-col items-center justify-center gap-2 border-danger text-danger hover:bg-danger/10">
                <AlertCircle className="h-6 w-6" />
                <span>Report Issue</span>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* My Tasks */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5 text-accent" />
              My Tasks Today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {tasksLoading ? <Skeleton className="h-20" /> : 
                (!tasks || tasks.length === 0) ? (
                  <p className="text-secondary text-sm">No tasks assigned.</p>
                ) : (
                  tasks.map((task: any) => (
                    <div key={task.id} className="flex items-center justify-between p-3 bg-surface border border-border rounded-lg">
                      <div>
                        <p className="text-sm font-bold text-primary capitalize">{task.type.replace('_', ' ')}</p>
                        <p className="text-xs text-secondary">{task.description || 'No description'}</p>
                        <span className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full mt-1 inline-block ${
                          task.status === 'done' ? 'bg-success/20 text-success' :
                          task.status === 'in_progress' ? 'bg-accent/20 text-accent' :
                          'bg-border text-secondary'
                        }`}>
                          {task.status.replace('_', ' ')}
                        </span>
                      </div>
                      
                      {task.status === 'todo' && (
                        <Button variant="primary" className="py-1 px-3 text-xs h-auto" onClick={() => updateStatus.mutate({ taskId: task.id, status: 'in_progress' })}>Start</Button>
                      )}
                      {task.status === 'in_progress' && (
                        <Button variant="success" className="py-1 px-3 text-xs h-auto" onClick={() => updateStatus.mutate({ taskId: task.id, status: 'done' })}>Finish</Button>
                      )}
                    </div>
                  ))
                )}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-success" />
              My Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activityLoading ? <Skeleton className="h-20" /> : 
                (!activity || (activity.movements.length === 0 && activity.cycle_counts.length === 0)) ? (
                  <p className="text-secondary text-sm">No recent activity.</p>
                ) : (
                  <>
                    {activity.movements.slice(0, 5).map((m: any) => (
                      <div key={`m-${m.id}`} className="text-sm p-3 bg-background rounded-lg border border-border flex justify-between">
                        <div>
                          <span className="font-semibold text-primary capitalize">{m.reason.replace('_', ' ')}</span>
                          <span className="text-secondary ml-2">Product #{m.product_id}</span>
                        </div>
                        <span className={`font-mono ${m.change_qty > 0 ? 'text-success' : 'text-danger'}`}>
                          {m.change_qty > 0 ? '+' : ''}{m.change_qty}
                        </span>
                      </div>
                    ))}
                    {activity.cycle_counts.slice(0, 5).map((c: any) => (
                      <div key={`c-${c.id}`} className="text-sm p-3 bg-background rounded-lg border border-border flex justify-between">
                        <div>
                          <span className="font-semibold text-primary">Cycle Count</span>
                          <span className="text-secondary ml-2">Product #{c.product_id}</span>
                        </div>
                        <span className="font-mono text-accent">
                          Counted: {c.counted_qty} (Var: {c.variance})
                        </span>
                      </div>
                    ))}
                  </>
                )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
