import React from 'react';

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  className = ''
}) {
  const variants = {
    default: 'bg-surface-container text-on-surface-variant border-transparent',
    primary: 'bg-primary/10 text-primary border-primary/20',
    success: 'bg-emerald-50 text-tertiary border-emerald-200',
    warning: 'bg-amber-50 text-amber-800 border-amber-200',
    error: 'bg-red-50 text-error border-red-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    secondary: 'bg-secondary/10 text-secondary border-secondary/20',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200'
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[11px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm'
  };

  // Helper mapping for student statuses
  let resolvedVariant = variant;
  const childText = typeof children === 'string' ? children.toLowerCase() : '';
  if (variant === 'status') {
    if (childText.includes('active') || childText.includes('present') || childText.includes('submitted')) resolvedVariant = 'success';
    else if (childText.includes('risk') || childText.includes('absent') || childText.includes('failed')) resolvedVariant = 'error';
    else if (childText.includes('late') || childText.includes('pending') || childText.includes('draft') || childText.includes('medium')) resolvedVariant = 'warning';
    else resolvedVariant = 'neutral';
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${variants[resolvedVariant] || variants.default} ${sizes[size] || sizes.md} ${className}`}
    >
      {dot && (
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            resolvedVariant === 'success' ? 'bg-emerald-500' :
            resolvedVariant === 'error' ? 'bg-red-500' :
            resolvedVariant === 'warning' ? 'bg-amber-500' :
            resolvedVariant === 'primary' ? 'bg-primary' : 'bg-slate-400'
          }`}
        />
      )}
      {children}
    </span>
  );
}

export default Badge;
