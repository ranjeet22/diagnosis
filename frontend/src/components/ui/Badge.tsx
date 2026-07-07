import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'primary',
  className = '',
}) => {
  const baseStyle = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold tracking-wide border';
  
  const variantStyles = {
    primary: 'bg-blue-50/50 text-primary border-blue-100',
    secondary: 'bg-slate-50 text-textSecondary border-slate-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    warning: 'bg-amber-50 text-amber-700 border-amber-100',
    danger: 'bg-rose-50 text-rose-700 border-rose-100',
    info: 'bg-sky-50 text-sky-700 border-sky-100',
  };

  return (
    <span className={`${baseStyle} ${variantStyles[variant]} ${className}`}>
      {children}
    </span>
  );
};
