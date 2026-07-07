import React from 'react';
import { motion } from 'framer-motion';

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className = '',
}) => {
  return (
    <div className={`flex space-x-1 p-1 bg-slate-100 rounded-full w-fit ${className}`}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className="relative flex items-center space-x-2 px-5 py-2 rounded-full text-xs font-semibold focus:outline-none transition-colors"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            {isActive && (
              <motion.span
                layoutId="bubble"
                className="absolute inset-0 bg-white shadow-sm border border-slate-200/50 rounded-full"
                transition={{ type: 'spring', bounce: 0.18, duration: 0.45 }}
              />
            )}
            <span className={`relative z-10 flex items-center space-x-1.5 ${isActive ? 'text-primary' : 'text-textSecondary hover:text-textPrimary'}`}>
              {tab.icon && <span className="w-4 h-4">{tab.icon}</span>}
              <span>{tab.label}</span>
            </span>
          </button>
        );
      })}
    </div>
  );
};
