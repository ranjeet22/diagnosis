import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

interface AccordionItem {
  title: string;
  content: string;
}

interface AccordionProps {
  items: AccordionItem[];
}

export const Accordion: React.FC<AccordionProps> = ({ items }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleItem = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className="space-y-3 w-full">
      {items.map((item, index) => {
        const isExpanded = expandedIndex === index;
        return (
          <div
            key={index}
            className="border border-slate-200/80 rounded-2xl bg-white/70 overflow-hidden shadow-sm transition-all duration-300"
          >
            <button
              onClick={() => toggleItem(index)}
              className="w-full flex items-center justify-between px-6 py-4.5 text-left font-medium text-textPrimary hover:bg-slate-50/50 transition-colors focus:outline-none"
            >
              <span>{item.title}</span>
              <motion.span
                animate={{ rotate: isExpanded ? 180 : 0 }}
                transition={{ duration: 0.25 }}
                className="text-textSecondary"
              >
                <ChevronDown className="w-5 h-5" />
              </motion.span>
            </button>

            <AnimatePresence initial={false}>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25, ease: 'easeInOut' }}
                >
                  <div className="px-6 pb-5 text-sm text-textSecondary leading-relaxed border-t border-slate-100 pt-3">
                    {item.content}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
};
