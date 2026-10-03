import React from 'react';

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  icon: Icon,
  iconPosition = 'left',
  disabled = false,
  onClick,
  type = 'button',
  ...props
}) {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none cursor-pointer';

  const variants = {
    primary: 'bg-primary text-white hover:bg-[#003da8] active:bg-[#003185] focus:ring-primary shadow-sm',
    container: 'bg-primary-container text-white hover:bg-blue-700 active:bg-blue-800 focus:ring-primary-container shadow-sm',
    secondary: 'bg-[#dae2fd] text-[#131b2e] hover:bg-[#c7d5fc] active:bg-[#b5c7fb] focus:ring-[#565e74]',
    outline: 'border border-outline-variant bg-white text-on-surface hover:bg-surface-container-low active:bg-surface-container focus:ring-primary',
    ghost: 'text-on-surface hover:bg-surface-container active:bg-surface-container-high focus:ring-primary',
    danger: 'bg-error text-white hover:bg-[#991414] active:bg-[#7a0f0f] focus:ring-error shadow-sm',
    success: 'bg-tertiary text-white hover:bg-[#005036] active:bg-[#003e29] focus:ring-tertiary shadow-sm',
    tertiaryFixed: 'bg-[#6ffbbe] text-[#002113] hover:bg-[#52ebb0] active:bg-[#34db9e] font-semibold',
    white: 'bg-white text-primary hover:bg-blue-50 active:bg-blue-100 focus:ring-white shadow-sm font-semibold'
  };

  const sizes = {
    sm: 'px-2.5 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-5 py-2.5 text-base gap-2.5',
    icon: 'p-2 text-sm'
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${baseStyles} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}
      {...props}
    >
      {Icon && iconPosition === 'left' && <Icon className="w-4 h-4 flex-shrink-0" />}
      {children}
      {Icon && iconPosition === 'right' && <Icon className="w-4 h-4 flex-shrink-0" />}
    </button>
  );
}

export default Button;
