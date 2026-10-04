import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { getSystemSettings, updateSystemSettings } from '../lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { JobsMonitor } from './JobsMonitor';

export function SystemSettings() {
  const [activeTab, setActiveTab] = useState<'settings' | 'jobs'>('settings');
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState<Record<string, string>>({});

  const { data, isLoading } = useQuery({
    queryKey: ['admin-settings'],
    queryFn: getSystemSettings
  });

  useEffect(() => {
    if (data) {
      setSettings(data);
    }
  }, [data]);

  const updateMutation = useMutation({
    mutationFn: (data: any) => updateSystemSettings(data),
    onSuccess: () => {
      toast.success('Settings updated');
      queryClient.invalidateQueries({ queryKey: ['admin-settings'] });
    },
    onError: () => toast.error('Failed to update settings')
  });

  const handleChange = (key: string, value: string) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(settings);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-serif text-primary">System Settings & Automation</h1>
        <div className="flex bg-surface border border-border p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'settings' ? 'bg-primary text-surface' : 'text-secondary hover:text-primary'}`}
          >
            Settings
          </button>
          <button
            onClick={() => setActiveTab('jobs')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'jobs' ? 'bg-primary text-surface' : 'text-secondary hover:text-primary'}`}
          >
            Jobs Monitor
          </button>
        </div>
      </div>
      
      {activeTab === 'settings' && (
        isLoading ? <div className="p-6"><Skeleton className="h-64" /></div> : (
          <form onSubmit={handleSave} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Automation Controls</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Global Kill Switch</label>
                  <select 
                    value={settings.global_kill_switch || 'false'} 
                    onChange={e => handleChange('global_kill_switch', e.target.value)}
                    className="w-full bg-surface border border-border rounded-md px-3 py-2 outline-none"
                  >
                    <option value="false">Active (Normal Operation)</option>
                    <option value="true">KILLED (Halt All Operations)</option>
                  </select>
                  <p className="text-xs text-secondary mt-1">If true, completely stops automated PO generation.</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Daily Spend Limit ($)</label>
                  <input 
                    type="number" 
                    value={settings.daily_spend_limit || '0'} 
                    onChange={e => handleChange('daily_spend_limit', e.target.value)}
                    className="w-full bg-surface border border-border rounded-md px-3 py-2 outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Auto-send Caps</label>
                  <input 
                    type="number" 
                    value={settings.auto_send_caps || '0'} 
                    onChange={e => handleChange('auto_send_caps', e.target.value)}
                    className="w-full bg-surface border border-border rounded-md px-3 py-2 outline-none"
                  />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>General Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Email Provider Config</label>
                  <select 
                    value={settings.email_configured || 'false'} 
                    onChange={e => handleChange('email_configured', e.target.value)}
                    className="w-full bg-surface border border-border rounded-md px-3 py-2 outline-none"
                  >
                    <option value="false">Not Configured</option>
                    <option value="true">Configured</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Session Length (Minutes)</label>
                  <input 
                    type="number" 
                    value={settings.session_length_minutes || '60'} 
                    onChange={e => handleChange('session_length_minutes', e.target.value)}
                    className="w-full bg-surface border border-border rounded-md px-3 py-2 outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Import Limits (Rows)</label>
                  <input 
                    type="number" 
                    value={settings.import_limits || '5000'} 
                    onChange={e => handleChange('import_limits', e.target.value)}
                    className="w-full bg-surface border border-border rounded-md px-3 py-2 outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">SMTP Password (Secret)</label>
                  <input 
                    type="text" 
                    value={settings.smtp_password || ''} 
                    onChange={e => handleChange('smtp_password', e.target.value)}
                    className="w-full bg-surface border border-border rounded-md px-3 py-2 outline-none"
                  />
                  <p className="text-xs text-secondary mt-1">Secrets are never displayed. Leave as ******** to keep unchanged.</p>
                </div>
              </CardContent>
            </Card>
            
            <div className="flex justify-end pt-4">
              <button 
                type="submit" 
                disabled={updateMutation.isPending}
                className="px-6 py-2 bg-accent text-white rounded hover:bg-accent/90 disabled:opacity-50"
              >
                Save Configuration
              </button>
            </div>
          </form>
        )
      )}

      {activeTab === 'jobs' && <JobsMonitor />}
    </div>
  );
}
