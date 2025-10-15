/**
 * Spinner Component
 *
 * Minimal loading indicator with smooth rotation animation.
 * Uses Tailwind CSS and Framer Motion for refined motion.
 *
 * Props:
 * - size: 'sm' | 'md' | 'lg' | 'xl' (default: 'md')
 * - color: 'primary' | 'neutral' | 'white' (default: 'primary')
 * - className: string - Additional custom classes
 */

import React from 'react';
import { motion } from 'framer-motion';

const Spinner = ({ size = 'md', color = 'primary', className = '' }) => {
  /**
   * Size configurations (width, height, border thickness)
   */
  const sizeStyles = {
    sm: 'w-4 h-4 border-2',
    md: 'w-5 h-5 border-2',
    lg: 'w-8 h-8 border-3',
    xl: 'w-12 h-12 border-4',
  };

  /**
   * Color variants for different contexts
   */
  const colorStyles = {
    primary: 'border-primary-500 border-t-transparent',
    neutral: 'border-neutral-400 border-t-transparent',
    white: 'border-white border-t-transparent',
  };

  /**
   * Smooth continuous rotation animation
   */
  const spinTransition = {
    duration: 0.8,
    ease: 'linear',
    repeat: Infinity,
  };

  return (
    <motion.div
      className={`
        inline-block rounded-full
        ${sizeStyles[size]}
        ${colorStyles[color]}
        ${className}
      `}
      animate={{ rotate: 360 }}
      transition={spinTransition}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </motion.div>
  );
};

export default Spinner;
