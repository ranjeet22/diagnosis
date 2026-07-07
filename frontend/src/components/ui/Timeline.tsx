import React from 'react';
import { motion } from 'framer-motion';
import { slideUp } from '../../animations/animations';

interface TimelineStep {
  title: string;
  description: string;
  step_number: string;
  icon?: React.ReactNode;
}

interface TimelineProps {
  steps: TimelineStep[];
}

export const Timeline: React.FC<TimelineProps> = ({ steps }) => {
  return (
    <div className="relative border-l border-slate-200/80 ml-4 md:ml-6 space-y-12">
      {steps.map((step, index) => (
        <motion.div
          key={index}
          className="relative pl-8 md:pl-10 group"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
          variants={slideUp(0.6, index * 0.15) as any}
        >
          {/* Step Number Dot indicator */}
          <div className="absolute -left-4 top-1 w-8 h-8 rounded-full bg-blue-50 border border-slate-200 text-primary flex items-center justify-center font-bold text-xs group-hover:bg-primary group-hover:text-white group-hover:border-primary transition-all duration-300">
            {step.icon ? step.icon : step.step_number}
          </div>

          <h3 className="text-base font-bold text-textPrimary mb-1.5 transition-colors group-hover:text-primary duration-300">
            {step.title}
          </h3>
          <p className="text-sm text-textSecondary leading-relaxed max-w-2xl">
            {step.description}
          </p>
        </motion.div>
      ))}
    </div>
  );
};
