/**
 * ConfidenceIndicator Component
 *
 * Visual confidence score display with color-coded status.
 * Shows percentage with progress bar or circular indicator.
 *
 * Props:
 * - value: number - Confidence score (0-100)
 * - size: 'sm' | 'md' | 'lg' - Size variant
 * - variant: 'bar' | 'badge' | 'circular' - Display style
 * - showPercentage: boolean - Show numeric percentage
 * - showTooltip: boolean - Show explanation tooltip
 * - className: string - Additional custom classes
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { formatConfidence } from '../../utils/formatters';

const ConfidenceIndicator = ({
  value,
  size = 'md',
  variant = 'badge',
  showPercentage = true,
  showTooltip = true,
  className = '',
}) => {
  const [showExplanation, setShowExplanation] = useState(false);

  // Format confidence
  const { percentage, status, color } = formatConfidence(value);

  /**
   * Size configurations
   */
  const sizes = {
    sm: {
      text: 'text-xs',
      padding: 'px-2 py-0.5',
      barHeight: 'h-1',
      circularSize: 'w-8 h-8',
    },
    md: {
      text: 'text-sm',
      padding: 'px-2.5 py-1',
      barHeight: 'h-2',
      circularSize: 'w-12 h-12',
    },
    lg: {
      text: 'text-base',
      padding: 'px-3 py-1.5',
      barHeight: 'h-3',
      circularSize: 'w-16 h-16',
    },
  };

  const sizeConfig = sizes[size];

  /**
   * Status-based styling
   */
  const statusStyles = {
    high: {
      bg: 'bg-success-light dark:bg-success-dark/20',
      border: 'border-success-DEFAULT dark:border-success-dark',
      text: 'text-success-dark dark:text-success-DEFAULT',
      bar: 'bg-success-DEFAULT',
    },
    medium: {
      bg: 'bg-warning-light dark:bg-warning-dark/20',
      border: 'border-warning-DEFAULT dark:border-warning-dark',
      text: 'text-warning-dark dark:text-warning-DEFAULT',
      bar: 'bg-warning-DEFAULT',
    },
    low: {
      bg: 'bg-error-light dark:bg-error-dark/20',
      border: 'border-error-DEFAULT dark:border-error-dark',
      text: 'text-error-dark dark:text-error-DEFAULT',
      bar: 'bg-error-DEFAULT',
    },
    unknown: {
      bg: 'bg-neutral-100 dark:bg-neutral-800',
      border: 'border-neutral-300 dark:border-neutral-700',
      text: 'text-neutral-600 dark:text-neutral-400',
      bar: 'bg-neutral-400',
    },
  };

  const style = statusStyles[status] || statusStyles.unknown;

  /**
   * Render badge variant
   */
  if (variant === 'badge') {
    return (
      <div className={`relative inline-flex ${className}`}>
        <motion.div
          className={`
            inline-flex items-center gap-1.5 rounded-md border
            ${sizeConfig.padding} ${sizeConfig.text}
            ${style.bg} ${style.border} ${style.text}
            font-medium
          `}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.2 }}
          onMouseEnter={() => showTooltip && setShowExplanation(true)}
          onMouseLeave={() => setShowExplanation(false)}
        >
          {/* Status Dot */}
          <div className={`w-1.5 h-1.5 rounded-full ${style.bar}`} />

          {/* Percentage */}
          {showPercentage && <span>{percentage}</span>}
        </motion.div>

        {/* Tooltip */}
        {showTooltip && showExplanation && (
          <motion.div
            className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-neutral-900 dark:bg-neutral-800 text-white text-xs rounded-lg shadow-lg whitespace-nowrap z-10"
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            transition={{ duration: 0.15 }}
          >
            Confidence: {getConfidenceLabel(status)}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
              <div className="border-4 border-transparent border-t-neutral-900 dark:border-t-neutral-800" />
            </div>
          </motion.div>
        )}
      </div>
    );
  }

  /**
   * Render progress bar variant
   */
  if (variant === 'bar') {
    return (
      <div className={`w-full ${className}`}>
        <div className="flex items-center justify-between mb-1">
          <span className={`${sizeConfig.text} ${style.text} font-medium`}>
            Confidence
          </span>
          <span className={`${sizeConfig.text} ${style.text} font-semibold`}>
            {percentage}
          </span>
        </div>

        {/* Progress Bar */}
        <div
          className={`
            w-full ${sizeConfig.barHeight} rounded-full overflow-hidden
            bg-neutral-200 dark:bg-neutral-700
          `}
        >
          <motion.div
            className={`h-full ${style.bar} rounded-full`}
            initial={{ width: 0 }}
            animate={{ width: `${value}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>
      </div>
    );
  }

  /**
   * Render circular variant
   */
  if (variant === 'circular') {
    const circumference = 2 * Math.PI * 16; // radius = 16
    const strokeDashoffset = circumference - (value / 100) * circumference;

    return (
      <div className={`relative inline-flex ${className}`}>
        <svg className={sizeConfig.circularSize} viewBox="0 0 36 36">
          {/* Background Circle */}
          <circle
            cx="18"
            cy="18"
            r="16"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            className="text-neutral-200 dark:text-neutral-700"
          />

          {/* Progress Circle */}
          <motion.circle
            cx="18"
            cy="18"
            r="16"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            className={style.text}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            transform="rotate(-90 18 18)"
          />
        </svg>

        {/* Centered Percentage */}
        {showPercentage && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`${sizeConfig.text} ${style.text} font-bold`}>
              {Math.round(value)}
            </span>
          </div>
        )}
      </div>
    );
  }

  return null;
};

/**
 * Get confidence label from status
 */
const getConfidenceLabel = (status) => {
  const labels = {
    high: 'High (e90%)',
    medium: 'Medium (70-89%)',
    low: 'Low (<70%)',
    unknown: 'Unknown',
  };

  return labels[status] || labels.unknown;
};

export default ConfidenceIndicator;
