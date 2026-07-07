import React, { useEffect, useRef } from 'react';
import { useMotionValue, useTransform, animate } from 'framer-motion';

interface AnimatedCounterProps {
  value: number;
  suffix?: string;
  prefix?: string;
  duration?: number;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  suffix = '',
  prefix = '',
  duration = 2,
}) => {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const controls = animate(count, value, {
      duration,
      ease: [0.16, 1, 0.3, 1], // easeOutExpo
    });
    return controls.stop;
  }, [value, duration]);

  useEffect(() => {
    return rounded.on('change', (latest) => {
      if (ref.current) {
        ref.current.textContent = prefix + latest.toLocaleString() + suffix;
      }
    });
  }, [rounded, prefix, suffix]);

  return (
    <span ref={ref} className="font-semibold tabular-nums">
      {prefix}0{suffix}
    </span>
  );
};
