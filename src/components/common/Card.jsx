import React from 'react';

export function Card({
  children,
  className = '',
  title,
  subtitle,
  headerAction,
  footer,
  padding = 'normal',
  ...props
}) {
  const paddings = {
    none: 'p-0',
    sm: 'p-4',
    normal: 'p-6',
    lg: 'p-8'
  };

  return (
    <div
      className={`bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-soft transition-all duration-200 ${className}`}
      {...props}
    >
      {(title || subtitle || headerAction) && (
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/40">
          <div>
            {title && <h3 className="font-display font-semibold text-lg text-on-surface">{title}</h3>}
            {subtitle && <p className="text-xs text-on-surface-variant mt-0.5">{subtitle}</p>}
          </div>
          {headerAction && <div className="flex items-center gap-2">{headerAction}</div>}
        </div>
      )}
      <div className={paddings[padding] || paddings.normal}>
        {children}
      </div>
      {footer && (
        <div className="px-6 py-3 bg-surface-container-low/60 border-t border-outline-variant/40 rounded-b-xl flex items-center justify-between text-xs text-on-surface-variant">
          {footer}
        </div>
      )}
    </div>
  );
}

export function StatCard({
  title,
  value,
  change,
  trend = 'up',
  period,
  icon: Icon,
  color = 'primary',
  className = ''
}) {
  const colorMap = {
    primary: {
      bg: 'bg-primary/10 text-primary',
      accent: 'text-primary'
    },
    tertiary: {
      bg: 'bg-tertiary/10 text-tertiary',
      accent: 'text-tertiary'
    },
    secondary: {
      bg: 'bg-secondary/10 text-secondary',
      accent: 'text-secondary'
    },
    error: {
      bg: 'bg-error/10 text-error',
      accent: 'text-error'
    }
  };

  const trendColors = {
    up: 'text-tertiary bg-emerald-50 border border-emerald-200',
    down: 'text-error bg-red-50 border border-red-200',
    alert: 'text-amber-700 bg-amber-50 border border-amber-200',
    neutral: 'text-secondary bg-slate-100 border border-slate-200'
  };

  const selectedColor = colorMap[color] || colorMap.primary;

  return (
    <div className={`bg-surface-container-lowest border border-outline-variant/60 rounded-xl p-5 shadow-soft hover:shadow-card transition-all duration-200 ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-on-surface-variant">{title}</p>
          <h3 className="font-display text-2xl md:text-3xl font-bold text-on-surface mt-2 tracking-tight">{value}</h3>
        </div>
        {Icon && (
          <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${selectedColor.bg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {(change || period) && (
        <div className="flex items-center gap-2 mt-4 text-xs">
          {change && (
            <span className={`px-2 py-0.5 rounded-full font-medium ${trendColors[trend] || trendColors.neutral}`}>
              {change}
            </span>
          )}
          {period && <span className="text-on-surface-variant">{period}</span>}
        </div>
      )}
    </div>
  );
}

export default Card;
