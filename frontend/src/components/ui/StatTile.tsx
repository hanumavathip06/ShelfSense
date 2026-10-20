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
}