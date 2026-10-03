import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import Button from './Button';

export function Pagination({
  currentPage = 1,
  totalPages = 1,
  totalItems = 0,
  pageSize = 10,
  onPageChange,
  className = ''
}) {
  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  return (
    <div className={`flex flex-col sm:flex-row items-center justify-between gap-4 px-4 py-3 bg-surface-container-lowest border-t border-outline-variant/40 ${className}`}>
      <div className="text-xs text-on-surface-variant">
        Showing <span className="font-semibold text-on-surface">{startItem}</span> to <span className="font-semibold text-on-surface">{endItem}</span> of <span className="font-semibold text-on-surface">{totalItems}</span> results
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage <= 1}
          onClick={() => onPageChange?.(currentPage - 1)}
          icon={ChevronLeft}
        >
          Previous
        </Button>

        <div className="flex items-center gap-1">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => onPageChange?.(page)}
              className={`w-8 h-8 rounded-lg text-xs font-semibold transition-colors ${
                currentPage === page
                  ? 'bg-primary text-white shadow-xs'
                  : 'text-on-surface hover:bg-surface-container'
              }`}
            >
              {page}
            </button>
          ))}
        </div>

        <Button
          variant="outline"
          size="sm"
          disabled={currentPage >= totalPages}
          onClick={() => onPageChange?.(currentPage + 1)}
          icon={ChevronRight}
          iconPosition="right"
        >
          Next
        </Button>
      </div>
    </div>
  );
}

export default Pagination;
