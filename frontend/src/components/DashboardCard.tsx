import React from 'react';

interface DashboardCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: string;
  variant?: 'default' | 'warning' | 'danger' | 'success';
  icon?: React.ReactNode;
}

export const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  variant = 'default',
  icon
}) => {
  const getTheme = () => {
    switch (variant) {
      case 'warning':
        return {
          cardBg: 'bg-amber-50/50 hover:bg-amber-50 border-amber-200',
          accent: 'text-amber-700 bg-amber-100 border-amber-300',
          valueColor: 'text-amber-950',
          indicator: 'bg-amber-500'
        };
      case 'danger':
        return {
          cardBg: 'bg-red-50/50 hover:bg-red-50 border-red-200',
          accent: 'text-red-700 bg-red-100 border-red-300',
          valueColor: 'text-red-950',
          indicator: 'bg-red-500'
        };
      case 'success':
        return {
          cardBg: 'bg-emerald-50/50 hover:bg-emerald-50 border-emerald-200',
          accent: 'text-emerald-700 bg-emerald-100 border-emerald-300',
          valueColor: 'text-emerald-950',
          indicator: 'bg-emerald-500'
        };
      default:
        return {
          cardBg: 'bg-white hover:bg-slate-50/80 border-slate-200',
          accent: 'text-slate-700 bg-slate-100 border-slate-300',
          valueColor: 'text-slate-900',
          indicator: 'bg-emerald-600'
        };
    }
  };

  const theme = getTheme();

  return (
    <div className={`p-4 rounded-xl border transition-all duration-200 shadow-sm hover:shadow relative overflow-hidden ${theme.cardBg}`}>
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-500">
          {title}
        </span>
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${theme.indicator}`}></span>
          {trend && (
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-700 shadow-2xs">
              {trend}
            </span>
          )}
        </div>
      </div>

      <div className="mt-2.5 flex items-baseline justify-between">
        <span className={`text-2xl font-bold font-mono tracking-tight ${theme.valueColor}`}>
          {value}
        </span>
        {icon && <div className="text-slate-400 opacity-80">{icon}</div>}
      </div>

      {subtitle && (
        <p className="text-[11px] font-mono text-slate-500 mt-1.5 pt-1.5 border-t border-slate-100 flex items-center justify-between">
          <span>{subtitle}</span>
        </p>
      )}
    </div>
  );
};
