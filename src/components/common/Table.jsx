import React from 'react';

export function Table({ children, className = '' }) {
  return (
    <div className={`w-full overflow-x-auto rounded-xl border border-outline-variant/60 bg-surface-container-lowest ${className}`}>
      <table className="w-full text-left text-sm text-on-surface">
        {children}
      </table>
    </div>
  );
}

export function TableHead({ children, className = '' }) {
  return (
    <thead className={`bg-surface-container-low/70 border-b border-outline-variant/50 text-xs uppercase font-semibold text-on-surface-variant tracking-wider ${className}`}>
      {children}
    </thead>
  );
}

export function TableBody({ children, className = '' }) {
  return (
    <tbody className={`divide-y divide-outline-variant/30 ${className}`}>
      {children}
    </tbody>
  );
}

export function TableRow({ children, className = '', hoverable = true, onClick }) {
  return (
    <tr
      onClick={onClick}
      className={`transition-colors duration-150 ${hoverable ? 'hover:bg-surface-container/50' : ''} ${onClick ? 'cursor-pointer' : ''} ${className}`}
    >
      {children}
    </tr>
  );
}

export function TableCell({ children, className = '', as = 'td' }) {
  const Component = as;
  return (
    <Component className={`px-4 py-3.5 align-middle ${className}`}>
      {children}
    </Component>
  );
}

export default Table;
