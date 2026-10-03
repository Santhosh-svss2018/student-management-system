import React from 'react';

export function Tabs({
  tabs = [],
  activeTab,
  onChange,
  variant = 'underline',
  className = ''
}) {
  if (variant === 'pills') {
    return (
      <div className={`inline-flex p-1 bg-surface-container rounded-xl gap-1 ${className}`}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => onChange(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs md:text-sm font-medium transition-all duration-150 select-none ${
                isActive
                  ? 'bg-surface-container-lowest text-primary shadow-xs font-semibold'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {Icon && <Icon className="w-4 h-4" />}
              {tab.label}
              {tab.count !== undefined && (
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${isActive ? 'bg-primary-container text-white' : 'bg-surface-container-highest text-on-surface-variant'}`}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div className={`flex border-b border-outline-variant/50 gap-6 ${className}`}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        const Icon = tab.icon;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`flex items-center gap-2 pb-3 pt-1 text-sm font-medium border-b-2 transition-all duration-150 select-none relative ${
              isActive
                ? 'border-primary text-primary font-semibold'
                : 'border-transparent text-on-surface-variant hover:text-on-surface hover:border-outline-variant'
            }`}
          >
            {Icon && <Icon className="w-4 h-4" />}
            {tab.label}
            {tab.count !== undefined && (
              <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${isActive ? 'bg-primary/10 text-primary' : 'bg-surface-container text-on-surface-variant'}`}>
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export default Tabs;
