/**
 * Button Component
 *
 * Professional, accessible button with multiple variants and states.
 * Features smooth animations, loading states, and disabled handling.
 *
 * Props:
 * - variant: 'primary' | 'ghost' | 'outline' (default: 'primary')
 * - size: 'sm' | 'md' | 'lg' (default: 'md')
 * - loading: boolean - Shows spinner and disables interaction
 * - disabled: boolean - Disables button interaction
 * - fullWidth: boolean - Makes button span full width
 * - leftIcon: ReactNode - Icon positioned before text
 * - rightIcon: ReactNode - Icon positioned after text
 * - children: ReactNode - Button content
 * - onClick: Function - Click handler
 * - type: 'button' | 'submit' | 'reset' (default: 'button')
 * - className: string - Additional custom classes
 */

import React from 'react';
import { motion } from 'framer-motion';
import Spinner from './Spinner';

const Button = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  children,
  onClick,
  type = 'button',
  className = '',
  ...props
}) => {
  /**
   * Base styles shared across all variants
   */
  const baseStyles = `
    inline-flex items-center justify-center gap-2
    font-medium rounded-lg
    transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    ${fullWidth ? 'w-full' : ''}
  `;

  /**
   * Size variants - padding and font sizing
   */
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  /**
   * Variant styles - color schemes and effects
   */
  const variantStyles = {
    primary: `
      bg-primary-500 text-white
      hover:bg-primary-600 hover:shadow-md
      active:bg-primary-700
      dark:bg-primary-600 dark:hover:bg-primary-700
    `,
    ghost: `
      bg-transparent text-text-primary
      hover:bg-neutral-100 hover:text-text-primary
      active:bg-neutral-200
      dark:text-text-inverse dark:hover:bg-neutral-800
    `,
    outline: `
      bg-transparent border border-border-default text-text-primary
      hover:bg-neutral-50 hover:border-primary-500 hover:text-primary-600
      active:bg-neutral-100
      dark:text-text-inverse dark:border-border-dark
      dark:hover:bg-neutral-900 dark:hover:border-primary-600
    `,
  };

  /**
   * Icon size based on button size
   */
  const iconSize = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  /**
   * Motion variants for subtle animations
   */
  const motionVariants = {
    rest: { scale: 1 },
    hover: { scale: 1.02, transition: { duration: 0.2 } },
    tap: { scale: 0.98, transition: { duration: 0.1 } },
  };

  const isDisabled = disabled || loading;

  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      className={`
        ${baseStyles}
        ${sizeStyles[size]}
        ${variantStyles[variant]}
        ${className}
      `}
      variants={motionVariants}
      initial="rest"
      whileHover={!isDisabled ? 'hover' : 'rest'}
      whileTap={!isDisabled ? 'tap' : 'rest'}
      {...props}
    >
      {/* Loading spinner replaces left icon */}
      {loading && <Spinner size={size} />}

      {/* Left icon (hidden during loading) */}
      {!loading && leftIcon && (
        <span className={iconSize[size]}>{leftIcon}</span>
      )}

      {/* Button text content */}
      {children && <span>{children}</span>}

      {/* Right icon */}
      {!loading && rightIcon && (
        <span className={iconSize[size]}>{rightIcon}</span>
      )}
    </motion.button>
  );
};

export default Button;
