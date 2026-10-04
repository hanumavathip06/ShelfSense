import os

ui_dir = "d:/Shashi/ShelfSense/frontend/src/components/ui"
os.makedirs(ui_dir, exist_ok=True)

files = {
    "Button.tsx": """import React from 'react';
import { twMerge } from 'tailwind-merge';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
}

export function Button({ variant = 'primary', className, ...props }: ButtonProps) {
  const base = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:opacity-50 disabled:pointer-events-none px-4 py-2";
  const variants = {
    primary: "bg-primary text-white hover:bg-primary/90 shadow-sm",
    secondary: "bg-surface text-primary hover:bg-border border border-border",
    outline: "border border-primary text-primary hover:bg-primary/10",
    danger: "bg-danger text-white hover:bg-danger/90 shadow-sm",
  };
  return <button className={twMerge(base, variants[variant], className)} {...props} />;
}""",
    "Input.tsx": """import React from 'react';
import { twMerge } from 'tailwind-merge';

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={twMerge("flex w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-primary placeholder:text-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-not-allowed disabled:opacity-50 font-mono shadow-sm", className)}
      {...props}
    />
  );
});
Input.displayName = 'Input';""",
    "Card.tsx": """import React from 'react';
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
}""",
    "Badge.tsx": """import React from 'react';
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
}""",
    "StatTile.tsx": """import React from 'react';
import { Card, CardContent } from './Card';
import { twMerge } from 'tailwind-merge';

export function StatTile({ title, value, icon: Icon, color }: { title: string, value: string | number, icon: any, color?: string }) {
  return (
    <Card>
      <CardContent className="p-6 flex items-center space-x-4">
        <div className={twMerge("p-3 rounded-full bg-background border border-border", color)}>
          <Icon size={24} />
        </div>
        <div>
          <p className="text-[10px] tracking-widest text-secondary uppercase font-bold">{title}</p>
          <h4 className="text-2xl font-serif text-primary mt-1">{value}</h4>
        </div>
      </CardContent>
    </Card>
  );
}""",
    "DataTable.tsx": """import React from 'react';
import { twMerge } from 'tailwind-merge';

export function DataTable({ headers, children, className }: { headers: React.ReactNode[], children: React.ReactNode, className?: string }) {
  return (
    <div className={twMerge("w-full overflow-auto rounded-xl border border-border shadow-sm", className)}>
      <table className="w-full text-sm text-left">
        <thead className="bg-background text-secondary border-b border-border">
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="px-6 py-3 font-bold text-[10px] uppercase tracking-widest">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-surface">
          {children}
        </tbody>
      </table>
    </div>
  );
}"""
}

for name, content in files.items():
    with open(os.path.join(ui_dir, name), 'w', encoding='utf-8') as f:
        f.write(content)

print("Components generated.")
