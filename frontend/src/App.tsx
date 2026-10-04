import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth, Permission } from './contexts/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import React, { Suspense, lazy } from 'react';
import { FEATURE_FLAGS } from './lib/features';

const Login = lazy(() => import('./pages/Login').then(m => ({ default: m.Login })));
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const Inventory = lazy(() => import('./pages/Inventory').then(m => ({ default: m.Inventory })));
const Reports = lazy(() => import('./pages/Reports').then(m => ({ default: m.Reports })));
const Users = lazy(() => import('./pages/Users').then(m => ({ default: m.Users })));
const Forecast = lazy(() => import('./pages/Forecast').then(m => ({ default: m.Forecast })));
const SmartReorder = lazy(() => import('./pages/SmartReorder').then(m => ({ default: m.SmartReorder })));
const Classification = lazy(() => import('./pages/Classification').then(m => ({ default: m.Classification })));
const ImportData = lazy(() => import('./pages/ImportData').then(m => ({ default: m.ImportData })));
const StockMovements = lazy(() => import('./pages/StockMovements').then(m => ({ default: m.StockMovements })));
const LowStock = lazy(() => import('./pages/LowStock').then(m => ({ default: m.LowStock })));
const ReportIssue = lazy(() => import('./pages/ReportIssue').then(m => ({ default: m.ReportIssue })));
const Approvals = lazy(() => import('./pages/Approvals').then(m => ({ default: m.Approvals })));
const PurchaseOrders = lazy(() => import('./pages/PurchaseOrders').then(m => ({ default: m.PurchaseOrders })));
const Suppliers = lazy(() => import('./pages/Suppliers').then(m => ({ default: m.Suppliers })));
const ReorderSettings = lazy(() => import('./pages/ReorderSettings').then(m => ({ default: m.ReorderSettings })));
const Team = lazy(() => import('./pages/Team').then(m => ({ default: m.Team })));
const SystemSettings = lazy(() => import('./pages/SystemSettings').then(m => ({ default: m.SystemSettings })));
const AuditLog = lazy(() => import('./pages/AuditLog').then(m => ({ default: m.AuditLog })));
const StoresLocations = lazy(() => import('./pages/StoresLocations').then(m => ({ default: m.StoresLocations })));
import { Toaster } from 'react-hot-toast';

function ProtectedRoute({ children, requiredPermission }: { children: React.ReactNode, requiredPermission?: Permission }) {
  const { isAuthenticated, hasPermission } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    // Render a simple 403 page instead of redirecting
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-2">403 Forbidden</h2>
          <p className="text-secondary">You do not have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Suspense fallback={<div className="flex h-screen items-center justify-center text-primary">Loading App...</div>}>
                <AppLayout />
              </Suspense>
            </ProtectedRoute>
          }
        >
          <Route index element={<ProtectedRoute requiredPermission={Permission.DASHBOARD_VIEW}><Dashboard /></ProtectedRoute>} />
          <Route path="inventory" element={<ProtectedRoute requiredPermission={Permission.INVENTORY_VIEW}><Inventory /></ProtectedRoute>} />
          <Route path="movements" element={<ProtectedRoute requiredPermission={Permission.MOVEMENT_RECORD}><StockMovements /></ProtectedRoute>} />
          <Route path="low-stock" element={<ProtectedRoute requiredPermission={Permission.DASHBOARD_VIEW}><LowStock /></ProtectedRoute>} />
          <Route path="report-issue" element={<ProtectedRoute requiredPermission={Permission.DASHBOARD_VIEW}><ReportIssue /></ProtectedRoute>} />
          {FEATURE_FLAGS.ENABLE_APPROVALS && <Route path="approvals" element={<ProtectedRoute requiredPermission={Permission.ORDERS_APPROVE}><Approvals /></ProtectedRoute>} />}
          {FEATURE_FLAGS.ENABLE_PURCHASE_ORDERS && <Route path="purchase-orders" element={<ProtectedRoute requiredPermission={Permission.ORDERS_VIEW}><PurchaseOrders /></ProtectedRoute>} />}
          {FEATURE_FLAGS.ENABLE_SUPPLIERS && <Route path="suppliers" element={<ProtectedRoute requiredPermission={Permission.SETTINGS_EDIT}><Suppliers /></ProtectedRoute>} />}
          <Route path="reorder-settings" element={<ProtectedRoute requiredPermission={Permission.INVENTORY_EDIT}><ReorderSettings /></ProtectedRoute>} />
          <Route path="team" element={<ProtectedRoute requiredPermission={Permission.INVENTORY_EDIT}><Team /></ProtectedRoute>} />
          <Route path="reports" element={<ProtectedRoute requiredPermission={Permission.REPORTS_VIEW}><Reports /></ProtectedRoute>} />
          <Route path="import" element={<ProtectedRoute requiredPermission={Permission.IMPORTS_EXECUTE}><ImportData /></ProtectedRoute>} />
          <Route path="forecast" element={<ProtectedRoute requiredPermission={Permission.FORECAST_VIEW}><Forecast /></ProtectedRoute>} />
          <Route path="smart-reorder" element={<ProtectedRoute requiredPermission={Permission.FORECAST_VIEW}><SmartReorder /></ProtectedRoute>} />
          <Route path="classification" element={<ProtectedRoute requiredPermission={Permission.FORECAST_VIEW}><Classification /></ProtectedRoute>} />
          <Route 
            path="users" 
            element={
              <ProtectedRoute requiredPermission={Permission.USERS_MANAGE}>
                <Users />
              </ProtectedRoute>
            } 
          />
          <Route path="system-settings" element={<ProtectedRoute requiredPermission={Permission.SYSTEM_SETTINGS_EDIT}><SystemSettings /></ProtectedRoute>} />
          <Route path="audit-log" element={<ProtectedRoute requiredPermission={Permission.AUDIT_LOG_VIEW}><AuditLog /></ProtectedRoute>} />
          <Route path="locations" element={<ProtectedRoute requiredPermission={Permission.SYSTEM_SETTINGS_EDIT}><StoresLocations /></ProtectedRoute>} />
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster position="top-right" />
    </>
  );
}

export default App;
