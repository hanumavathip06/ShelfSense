import { useAuth } from '../contexts/AuthContext';
import { AdminDashboard } from './dashboards/AdminDashboard';
import { ManagerDashboard } from './dashboards/ManagerDashboard';
import { StaffDashboard } from './dashboards/StaffDashboard';

export function Dashboard() {
  const { user } = useAuth();
  
  if (!user) return null;
  
  if (user.role === 'admin') return <AdminDashboard />;
  if (user.role === 'manager') return <ManagerDashboard />;
  return <StaffDashboard />;
}
