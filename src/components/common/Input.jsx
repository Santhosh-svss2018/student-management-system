import React from 'react';

export function Input({
  label,
  error,
  helperText,
  icon: Icon,
  className = '',
  id,
  type = 'text',
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-on-surface mb-1.5">
          {label}
        </label>
      )}
      <div className="relative rounded-lg">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          id={inputId}
          type={type}
          className={`w-full bg-white border ${
            error ? 'border-error ring-1 ring-error/20' : 'border-outline-variant hover:border-outline focus:border-primary'
          } rounded-lg text-sm text-on-surface placeholder:text-on-surface-variant/60 py-2 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary/20 ${
            Icon ? 'pl-9 pr-3' : 'px-3'
          } ${className}`}
          {...props}
        />
      </div>
      {error ? (
        <p className="mt-1 text-xs text-error font-medium">{error}</p>
      ) : helperText ? (
        <p className="mt-1 text-xs text-on-surface-variant">{helperText}</p>
      ) : null}
    </div>
  );
}

export function Textarea({
  label,
  error,
  helperText,
  className = '',
  id,
  rows = 3,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-on-surface mb-1.5">
          {label}
        </label>
      )}
      <textarea
        id={inputId}
        rows={rows}
        className={`w-full bg-white border ${
          error ? 'border-error ring-1 ring-error/20' : 'border-outline-variant hover:border-outline focus:border-primary'
        } rounded-lg text-sm text-on-surface placeholder:text-on-surface-variant/60 p-3 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary/20 ${className}`}
        {...props}
      />
      {error ? (
        <p className="mt-1 text-xs text-error font-medium">{error}</p>
      ) : helperText ? (
        <p className="mt-1 text-xs text-on-surface-variant">{helperText}</p>
      ) : null}
    </div>
  );
}

export default Input;
