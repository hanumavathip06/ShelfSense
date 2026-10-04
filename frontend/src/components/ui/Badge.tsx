import React from 'react';
import { twMerge } from 'tailwind-merge';

export function Badge({ children, variant = 'default', className }: { children: React.ReactNode, variant?: 'default' | 'success' | 'warning' | 'danger', className?: string }) {
  const base = "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-mono tracking-wider transition-colors focus:outline-none focus:ring-2 focus:ring-accent";
  const variants = {
    default: "border-transparent bg-secondary text-white",
    success: "border-transparent bg-success text-white",
    warning: "border-transparent bg-warning text-white",
    danger: "border-transparent bg-danger text-white",
  };
  return <div className={twMerge(base, variants[variant], className)}>{children}</div>;
}