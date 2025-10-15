/**
 * Alert Component
 *
 * Professional alert/notification component with subtle styling.
 * Supports multiple types, auto-dismiss, and smooth animations.
 *
 * Props:
 * - type: 'success' | 'error' | 'warning' | 'info' (default: 'info')
 * - title: string - Optional alert title
 * - message: string - Alert message content
 * - dismissible: boolean - Shows close button (default: true)
 * - onClose: Function - Callback when alert is dismissed
 * - autoDismiss: number - Auto-dismiss after X milliseconds (0 = disabled)
 * - icon: ReactNode - Custom icon (overrides default type icon)
 * - className: string - Additional custom classes
 */

import React, { useEffect } from 'react';
import { motion } from 'framer-motion';

const Alert = ({
  type = 'info',
  title,
  message,
  dismissible = true,
  onClose,
  autoDismiss = 0,
  icon,
  className = '',
}) => {
  /**
   * Auto-dismiss logic
   */
  useEffect(() => {
    if (autoDismiss > 0 && onClose) {
      const timer = setTimeout(() => {
        onClose();
      }, autoDismiss);

      return () => clearTimeout(timer);
    }
  }, [autoDismiss, onClose]);

  /**
   * Type-based styling (desaturated enterprise tones)
   */
  const typeStyles = {
    success: {
      container: 'bg-success-light/20 border-success-DEFAULT/30 dark:bg-success-dark/10',
      icon: 'text-success-dark dark:text-success-DEFAULT',
      title: 'text-success-dark dark:text-success-DEFAULT',
      message: 'text-success-dark/80 dark:text-success-DEFAULT/80',
    },
    error: {
      container: 'bg-error-light/20 border-error-DEFAULT/30 dark:bg-error-dark/10',
      icon: 'text-error-dark dark:text-error-DEFAULT',
      title: 'text-error-dark dark:text-error-DEFAULT',
      message: 'text-error-dark/80 dark:text-error-DEFAULT/80',
    },
    warning: {
      container: 'bg-warning-light/20 border-warning-DEFAULT/30 dark:bg-warning-dark/10',
      icon: 'text-warning-dark dark:text-warning-DEFAULT',
      title: 'text-warning-dark dark:text-warning-DEFAULT',
      message: 'text-warning-dark/80 dark:text-warning-DEFAULT/80',
    },
    info: {
      container: 'bg-info-light/20 border-info-DEFAULT/30 dark:bg-info-dark/10',
      icon: 'text-info-dark dark:text-info-DEFAULT',
      title: 'text-info-dark dark:text-info-DEFAULT',
      message: 'text-info-dark/80 dark:text-info-DEFAULT/80',
    },
  };

  /**
   * Default icons for each type
   */
  const defaultIcons = {
    success: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    error: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    warning: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
    ),
    info: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  };

  /**
   * Animation variants for entrance and exit
   */
  const alertVariants = {
    hidden: {
      opacity: 0,
      y: -10,
      scale: 0.95,
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.3,
        ease: [0.4, 0, 0.2, 1],
      },
    },
    exit: {
      opacity: 0,
      x: 100,
      transition: {
        duration: 0.2,
        ease: [0.4, 0, 1, 1],
      },
    },
  };

  const styles = typeStyles[type];

  return (
    <motion.div
      className={`
        flex items-start gap-3 p-4 rounded-lg border
        ${styles.container}
        ${className}
      `}
      variants={alertVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      role="alert"
      aria-live="polite"
    >
      {/* Icon */}
      <div className={`flex-shrink-0 ${styles.icon}`}>
        {icon || defaultIcons[type]}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className={`text-sm font-semibold mb-1 ${styles.title}`}>
            {title}
          </h4>
        )}
        <p className={`text-sm ${styles.message}`}>
          {message}
        </p>
      </div>

      {/* Close button */}
      {dismissible && onClose && (
        <button
          onClick={onClose}
          className={`
            flex-shrink-0 p-1 rounded-md
            ${styles.icon}
            hover:bg-black/5 dark:hover:bg-white/5
            transition-colors duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-1
          `}
          aria-label="Dismiss alert"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </motion.div>
  );
};

export default Alert;
