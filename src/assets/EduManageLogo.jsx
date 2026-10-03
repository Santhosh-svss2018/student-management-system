import React from 'react';

export function EduManageLogo({ className = 'h-9 w-auto', showText = true, textClassName = 'text-slate-900 dark:text-white' }) {
  return (
    <div className={`flex items-center gap-3 select-none ${className}`}>
      <svg className="h-9 w-9 flex-shrink-0" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="48" height="48" rx="12" fill="#2563EB" />
        <path d="M24 14L11 21L24 28L37 21L24 14Z" fill="#FFFFFF" />
        <path d="M16 24.5V32C16 32 19.5 35 24 35C28.5 35 32 32 32 32V24.5L24 29.5L16 24.5Z" fill="#BFDBFE" />
        <circle cx="34.5" cy="25" r="2" fill="#93C5FD" />
        <path d="M34.5 27V34" stroke="#93C5FD" strokeWidth="2" strokeLinecap="round" />
      </svg>
      {showText && (
        <span className={`text-2xl font-bold tracking-tight font-display ${textClassName}`}>
          Edu<span className="text-primary-container">Manage</span>
        </span>
      )}
    </div>
  );
}

export default EduManageLogo;
