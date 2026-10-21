import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/axios';
import { useAuth } from '../contexts/AuthContext';
import { z } from 'zod';
import { Package } from 'lucide-react';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const cleanEmail = email.trim().toLowerCase();
    const result = loginSchema.safeParse({ email: cleanEmail, password });
    if (!result.success) {
      setError(result.error.issues[0].message);
      return;
    }

    setLoading(true);
    
    try {
      const response = await api.post('/auth/login', { email: cleanEmail, password });
      const { access_token, user } = response.data;
      login(access_token, user);
      navigate('/', { replace: true });
    } catch (err: any) {
      const msg = typeof err.response?.data?.error === 'string'
        ? err.response.data.error
        : (err.response?.data?.error?.message || err.response?.data?.message || 'Login failed. Please check your credentials.');
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Left sidebar panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-bg-dark bg-grid-pattern p-12 text-white border-r border-[#1B4237]">
        <div>
          <div className="flex items-center space-x-2 text-white/90">
            <div className="bg-white text-bg-dark p-1.5 rounded">
              <Package size={24} strokeWidth={1.5} />
            </div>
            <div>
              <span className="block font-bold leading-tight">TheShelfSense</span>
              <span className="block text-[10px] tracking-[0.2em] text-white/60 uppercase">Inventory OS</span>
            </div>
          </div>
        </div>
        <div className="max-w-md">
          <h1 className="text-4xl font-serif mb-6 leading-tight">
            Every shelf, every unit, one source of truth.
          </h1>
          <p className="text-white/70 font-sans text-sm leading-relaxed mb-12">
            Role-based access, real-time stock tracking and automated restocking workflows — built to remove manual errors before they reach the shelf.
          </p>
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="mt-1 p-1 rounded border border-white/20 bg-white/5">
                 <svg className="w-4 h-4 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
              </div>
              <div>
                <h3 className="font-semibold text-sm">Role-based access</h3>
                <p className="text-white/50 text-xs mt-1">Admin, manager and staff scopes enforced server-side</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="mt-1 p-1 rounded border border-white/20 bg-white/5">
                <svg className="w-4 h-4 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
              <div>
                <h3 className="font-semibold text-sm">Automated restocking</h3>
                <p className="text-white/50 text-xs mt-1">Draft orders queue themselves the moment stock hits reorder point</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="mt-1 p-1 rounded border border-white/20 bg-white/5">
                <svg className="w-4 h-4 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
              </div>
              <div>
                <h3 className="font-semibold text-sm">Historical logs</h3>
                <p className="text-white/50 text-xs mt-1">Every movement, approval and edit leaves an immutable trail</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 lg:p-24 bg-background">
        <div className="w-full max-w-[400px]">
          <h2 className="text-3xl font-serif text-primary mb-2 tracking-tight">
            Sign in to your workspace
          </h2>
          <p className="text-secondary text-sm mb-10">
            Use your operations account. Sessions stay active for seven days.
          </p>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="text-danger text-sm bg-danger/10 p-3 rounded border border-danger/20">
                {error}
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label htmlFor="email-address" className="block text-[10px] font-bold tracking-widest text-secondary uppercase mb-2">
                  Work Email
                </label>
                <input
                  id="email-address"
                  name="email"
                  type="email"
                  autoComplete="email"
                  className="block w-full rounded-md border border-border py-2.5 px-3 text-primary placeholder:text-secondary focus:outline-none focus:ring-2 focus:ring-accent sm:text-sm font-mono shadow-sm bg-white"
                  placeholder="you@shelfsense.io"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-[10px] font-bold tracking-widest text-secondary uppercase mb-2">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  className="block w-full rounded-md border border-border py-2.5 px-3 text-primary placeholder:text-secondary focus:outline-none focus:ring-2 focus:ring-accent sm:text-sm shadow-sm bg-white"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-accent px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-accent/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-50 transition-colors"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
