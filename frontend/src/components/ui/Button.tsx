import React from 'react';
import { motion } from 'framer-motion';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  animate?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  animate = true,
  className = '',
  ...props
}) => {
  const baseStyle = 'inline-flex items-center justify-center font-medium rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2';
  
  const sizeStyles = {
    sm: 'px-4 py-1.5 text-xs',
    md: 'px-6 py-2.5 text-sm',
    lg: 'px-8 py-3.5 text-base',
  };

  const variantStyles = {
    primary: 'bg-primary text-white hover:bg-blue-700 shadow-sm border border-transparent',
    secondary: 'bg-blue-50 text-primary hover:bg-blue-100 border border-transparent',
    outline: 'bg-transparent text-textPrimary hover:bg-slate-50 border border-slate-200',
    ghost: 'bg-transparent text-textSecondary hover:bg-slate-100 hover:text-textPrimary border border-transparent',
  };

  const combinedClassName = `${baseStyle} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`;

  if (!animate) {
    return (
      <button className={combinedClassName} {...props}>
        {children}
      </button>
    );
  }

  return (
    <motion.button
      className={combinedClassName}
      whileHover={{ scale: 1.02, y: -1 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      {...(props as any)}
    >
      {children}
    </motion.button>
  );
};
