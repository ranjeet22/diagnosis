import type { Variants } from 'framer-motion';

export const fadeIn = (duration = 0.5, delay = 0): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration, delay, ease: 'easeOut' },
  },
});

export const slideUp = (duration = 0.6, delay = 0): Variants => ({
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration, delay, ease: [0.215, 0.61, 0.355, 1] },
  },
});

export const slideDown = (duration = 0.6, delay = 0): Variants => ({
  hidden: { opacity: 0, y: -30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration, delay, ease: [0.215, 0.61, 0.355, 1] },
  },
});

export const slideLeft = (duration = 0.6, delay = 0): Variants => ({
  hidden: { opacity: 0, x: 40 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration, delay, ease: [0.215, 0.61, 0.355, 1] },
  },
});

export const slideRight = (duration = 0.6, delay = 0): Variants => ({
  hidden: { opacity: 0, x: -40 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration, delay, ease: [0.215, 0.61, 0.355, 1] },
  },
});

export const scaleIn = (duration = 0.5, delay = 0): Variants => ({
  hidden: { opacity: 0, scale: 0.93 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration, delay, ease: 'easeOut' },
  },
});

export const staggerContainer = (staggerChildren = 0.1, delayChildren = 0): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren,
      delayChildren,
    },
  },
});

export const blurReveal = (duration = 0.8, delay = 0): Variants => ({
  hidden: { opacity: 0, filter: 'blur(10px)', y: 20 },
  visible: {
    opacity: 1,
    filter: 'blur(0px)',
    y: 0,
    transition: { duration, delay, ease: 'easeOut' },
  },
});

export const floatingAnimation = (duration = 3): Variants => ({
  animate: {
    y: [0, -10, 0],
    transition: {
      duration,
      repeat: Infinity,
      repeatType: 'reverse',
      ease: 'easeInOut',
    },
  },
});

export const cardHoverLift: Variants = {
  hover: {
    y: -6,
    boxShadow: '0 12px 30px -4px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.04)',
    transition: { duration: 0.3, ease: 'easeOut' as any },
  },
};
