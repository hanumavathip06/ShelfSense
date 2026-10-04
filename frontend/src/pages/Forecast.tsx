import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, ResponsiveContainer, Area, AreaChart,
  BarChart, Bar, Legend,
  Line
} from 'recharts';
import { Brain, TrendingUp, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { getProducts, getForecast, compareModels, trainModels } from '../lib/api';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { useAuth } from '../contexts/AuthContext';

export function Forecast() {
  const { role } = useAuth();
  const queryClient = useQueryClient();
  const canTrain = role === 'admin' || role === 'manager';

  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [horizon, setHorizon] = useState(30);

  const { data: productsData } = useQuery({
    queryKey: ['products-all'],
    queryFn: () => getProducts({ limit: 100 }),
  });

  const { data: forecastData, isLoading: loadingForecast } = useQuery({
    queryKey: ['forecast', selectedProductId, horizon],
    queryFn: () => getForecast(selectedProductId!, horizon),
    enabled: !!selectedProductId,
  });

  const { data: comparisonData, isLoading: loadingComparison } = useQuery({
    queryKey: ['model-comparison', selectedProductId],
    queryFn: () => compareModels(selectedProductId!),
    enabled: !!selectedProductId,
  });

  const trainMutation = useMutation({
    mutationFn: () => trainModels(selectedProductId!, horizon),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forecast'] });
      queryClient.invalidateQueries({ queryKey: ['model-comparison'] });
      toast.success('Models trained successfully!');
    },
    onError: (err: any) => toast.error(err.response?.data?.error?.message || 'Training failed'),
  });

  // Prepare forecast chart data
  const forecastChartData = forecastData?.predictions
    ? forecastData.predictions.map((pred: number, idx: number) => ({
        day: `Day ${idx + 1}`,
        predicted: Math.round(pred * 100) / 100,
        lower: forecastData.confidence_lower?.[idx] ? Math.round(forecastData.confidence_lower[idx] * 100) / 100 : 0,
        upper: forecastData.confidence_upper?.[idx] ? Math.round(forecastData.confidence_upper[idx] * 100) / 100 : 0,
      }))
    : [];

  // Prepare model comparison chart data
  const comparisonChartData = comparisonData?.models?.map((m: any) => ({
    name: m.model_name,
    RMSE: m.rmse ? Math.round(m.rmse * 100) / 100 : 0,
    MAE: m.mae ? Math.round(m.mae * 100) / 100 : 0,
    MAPE: m.mape ? Math.round(m.mape * 100) / 100 : 0,
  })) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-accent/10 rounded-lg">
            <Brain className="h-6 w-6 text-accent" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-primary">AI Demand Forecast</h1>
            <p className="text-sm text-secondary">ML-powered demand prediction using ARIMA, Prophet, LSTM & XGBoost</p>
          </div>
        </div>
        {canTrain && selectedProductId && (
          <button
            onClick={() => trainMutation.mutate()}
            disabled={trainMutation.isPending}
            className="inline-flex items-center justify-center rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-50"
          >
            {trainMutation.isPending ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Training...</>
            ) : (
              <><TrendingUp className="mr-2 h-4 w-4" /> Train Models</>
            )}
          </button>
        )}
      </div>

      {/* Product & Horizon Selection */}
      <div className="flex flex-col sm:flex-row gap-4">
        <select
          className="flex-1 px-3 py-2 rounded-md border border-border bg-surface text-primary focus:ring-2 focus:ring-accent focus:outline-none"
          value={selectedProductId || ''}
          onChange={(e) => setSelectedProductId(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">Select a product to forecast...</option>
          {productsData?.items?.map((p: any) => (
            <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
          ))}
        </select>
        <select
          className="w-full sm:w-40 px-3 py-2 rounded-md border border-border bg-surface text-primary focus:ring-2 focus:ring-accent focus:outline-none"
          value={horizon}
          onChange={(e) => setHorizon(Number(e.target.value))}
        >
          <option value={7}>7 Days</option>
          <option value={14}>14 Days</option>
          <option value={30}>30 Days</option>
          <option value={60}>60 Days</option>
        </select>
      </div>

      {!selectedProductId ? (
        <EmptyState title="Select a Product" description="Choose a product from the dropdown to view its demand forecast." />
      ) : loadingForecast ? (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Skeleton className="h-96 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
      ) : forecastData?.message && !forecastData?.predictions ? (
        <div className="rounded-lg bg-surface border border-border shadow-sm p-8">
          <EmptyState
            title="Insufficient Data"
            description={forecastData.message || 'Not enough stock movement history. Train models first or add more stock movements.'}
          />
          {canTrain && (
            <div className="flex justify-center mt-4">
              <button
                onClick={() => trainMutation.mutate()}
                disabled={trainMutation.isPending}
                className="inline-flex items-center justify-center rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-50"
              >
                {trainMutation.isPending ? 'Training...' : 'Train Models Now'}
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Forecast Info Banner */}
          <div className="rounded-lg bg-accent/5 border border-accent/20 p-4 flex flex-wrap items-center gap-4">
            <div>
              <span className="text-sm text-secondary">Product:</span>
              <span className="ml-2 text-sm font-semibold text-primary">{forecastData?.product_name}</span>
            </div>
            <div>
              <span className="text-sm text-secondary">Model:</span>
              <span className="ml-2 text-sm font-semibold text-accent">{forecastData?.model_name || 'Hybrid Ensemble'}</span>
            </div>
            {forecastData?.metrics?.rmse != null && (
              <div>
                <span className="text-sm text-secondary">RMSE:</span>
                <span className="ml-2 text-sm font-semibold text-primary">{forecastData.metrics.rmse}</span>
              </div>
            )}
            {forecastData?.metrics?.mape != null && (
              <div>
                <span className="text-sm text-secondary">MAPE:</span>
                <span className="ml-2 text-sm font-semibold text-primary">{forecastData.metrics.mape}%</span>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Forecast Chart */}
            <div className="rounded-lg bg-surface border border-border shadow-sm p-6">
              <h3 className="text-lg font-medium text-primary mb-4">
                Demand Forecast ({horizon} Days)
              </h3>
              <div className="h-80">
                {forecastChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={forecastChartData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                      <XAxis dataKey="day" tick={{ fill: '#6B7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: '#6B7280' }} axisLine={false} tickLine={false} />
                      <RechartsTooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }} />
                      <Area type="monotone" dataKey="upper" stroke="none" fill="#4338CA" fillOpacity={0.1} name="Upper Bound" />
                      <Area type="monotone" dataKey="lower" stroke="none" fill="#ffffff" fillOpacity={0.8} name="Lower Bound" />
                      <Line type="monotone" dataKey="predicted" stroke="#4338CA" strokeWidth={3} dot={false} activeDot={{ r: 5 }} name="Predicted Demand" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyState title="No forecast data" description="Train models to generate predictions." />
                )}
              </div>
            </div>

            {/* Model Comparison */}
            <div className="rounded-lg bg-surface border border-border shadow-sm p-6">
              <h3 className="text-lg font-medium text-primary mb-4">Model Performance Comparison</h3>
              <div className="h-80">
                {loadingComparison ? (
                  <Skeleton className="h-full w-full" />
                ) : comparisonChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={comparisonChartData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E5E7EB" />
                      <XAxis type="number" tick={{ fill: '#6B7280' }} axisLine={false} tickLine={false} />
                      <YAxis dataKey="name" type="category" tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} width={120} />
                      <RechartsTooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }} />
                      <Legend />
                      <Bar dataKey="RMSE" fill="#4338CA" radius={[0, 4, 4, 0]} />
                      <Bar dataKey="MAE" fill="#059669" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyState title="No model data" description="Train models to see comparison metrics." />
                )}
              </div>
            </div>
          </div>

          {/* Metrics Table */}
          {comparisonData?.models && comparisonData.models.length > 0 && (
            <div className="rounded-lg bg-surface border border-border shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-border bg-background">
                <h3 className="text-lg font-medium text-primary">
                  Detailed Model Metrics
                  {comparisonData.best_model && (
                    <span className="ml-3 text-sm font-normal text-success">
                      Best: {comparisonData.best_model}
                    </span>
                  )}
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-border">
                  <thead className="bg-surface">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Model</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">RMSE</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">MAE</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">MAPE (%)</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">R² Score</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-secondary uppercase tracking-wider">Trained</th>
                    </tr>
                  </thead>
                  <tbody className="bg-surface divide-y divide-border">
                    {comparisonData.models.map((model: any, idx: number) => (
                      <tr key={model.model_name} className={idx === 0 ? 'bg-success/5' : ''}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary">
                          {model.model_name}
                          {idx === 0 && (
                            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success/10 text-success">
                              Best
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary text-right">{model.rmse?.toFixed(4) ?? '—'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary text-right">{model.mae?.toFixed(4) ?? '—'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary text-right">{model.mape?.toFixed(2) ?? '—'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary text-right">{model.r2_score?.toFixed(4) ?? '—'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary text-right">
                          {model.trained_at ? new Date(model.trained_at).toLocaleDateString() : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
