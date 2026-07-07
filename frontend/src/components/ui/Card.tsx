import React from 'react';
import { motion } from 'framer-motion';
import { cardHoverLift } from '../../animations/animations';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'glass' | 'floating';
  className?: string;
  animate?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  className = '',
  animate = true,
}) => {
  const baseStyle = 'rounded-2xl border transition-all duration-300';
  
  const variantStyles = {
    default: 'bg-white border-slate-200/80 shadow-soft',
    glass: 'glass-card',
    floating: 'bg-white border-slate-100 shadow-soft hover:shadow-lg',
  };

  const combinedClassName = `${baseStyle} ${variantStyles[variant]} ${className}`;

  if (!animate) {
    return <div className={combinedClassName}>{children}</div>;
  }

  return (
    <motion.div
      className={combinedClassName}
      variants={cardHoverLift}
      whileHover="hover"
    >
      {children}
    </motion.div>
  );
};
