import React from 'react';
import { ChevronDown } from 'lucide-react';

export function Select({
  label,
  options = [],
  value,
  onChange,
  error,
  helperText,
  className = '',
  id,
  placeholder = 'Select option...',
  ...props
}) {
  const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="block text-xs font-semibold text-on-surface mb-1.5">
          {label}
        </label>
      )}
      <div className="relative">
        <select
          id={selectId}
          value={value}
          onChange={onChange}
          className={`w-full appearance-none bg-white border ${
            error ? 'border-error ring-1 ring-error/20' : 'border-outline-variant hover:border-outline focus:border-primary'
          } rounded-lg text-sm text-on-surface py-2 pl-3 pr-9 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary/20 ${className}`}
          {...props}
        >
          {placeholder && <option value="">{placeholder}</option>}
          {options.map((opt, idx) => {
            const optVal = typeof opt === 'object' ? opt.value : opt;
            const optLabel = typeof opt === 'object' ? opt.label : opt;
            return (
              <option key={idx} value={optVal}>
                {optLabel}
              </option>
            );
          })}
        </select>
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-on-surface-variant">
          <ChevronDown className="w-4 h-4" />
        </div>
      </div>
      {error ? (
        <p className="mt-1 text-xs text-error font-medium">{error}</p>
      ) : helperText ? (
        <p className="mt-1 text-xs text-on-surface-variant">{helperText}</p>
      ) : null}
    </div>
  );
}

export default Select;
