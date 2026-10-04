import React from 'react';
import { twMerge } from 'tailwind-merge';

export function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={twMerge("rounded-xl border border-border bg-surface shadow-sm", className)}>{children}</div>;
}
export function CardHeader({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={twMerge("flex flex-col space-y-1.5 p-6", className)}>{children}</div>;
}
export function CardTitle({ className, children }: { className?: string; children: React.ReactNode }) {
  return <h3 className={twMerge("font-serif font-semibold leading-none tracking-tight text-primary", className)}>{children}</h3>;
}
export function CardContent({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={twMerge("p-6 pt-0", className)}>{children}</div>;
}