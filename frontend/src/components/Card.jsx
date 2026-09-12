import React from 'react';

export function Card({ children, className = '', title, subtitle, action, footer }) {
  return (
    <div className={`bg-white rounded-xl border border-slate-200 shadow-sm p-5 md:p-6 transition-colors ${className}`}>
      {(title || subtitle || action) && (
        <div className="flex items-start justify-between mb-4 border-b border-slate-100 pb-3">
          <div>
            {title && <h3 className="font-semibold text-slate-800 text-base md:text-lg">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div>{children}</div>
      {footer && <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500">{footer}</div>}
    </div>
  );
}
