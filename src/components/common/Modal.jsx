import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import Button from './Button';

export function Modal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  footer,
  maxWidth = 'max-w-lg',
  className = ''
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose?.();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="fixed inset-0"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className={`relative w-full ${maxWidth} bg-surface-container-lowest border border-outline-variant/60 rounded-2xl shadow-elevated z-10 overflow-hidden ${className}`}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/40">
          <div>
            {title && <h3 className="font-display font-bold text-lg text-on-surface">{title}</h3>}
            {subtitle && <p className="text-xs text-on-surface-variant mt-0.5">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-on-surface-variant hover:text-on-surface hover:bg-surface-container rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          {children}
        </div>

        {footer && (
          <div className="flex items-center justify-end gap-3 px-6 py-3 bg-surface-container-low/60 border-t border-outline-variant/40">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

export default Modal;
