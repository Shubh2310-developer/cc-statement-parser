/**
 * FieldDisplay Component
 *
 * Individual field renderer with icon, label, value, and confidence.
 * Supports copy-to-clipboard, tooltips, and highlighted variants.
 *
 * Props:
 * - label: string - Field label
 * - value: string - Field value
 * - confidence: number - Confidence score (0-1 or 0-100)
 * - snippet: string - Original text snippet
 * - icon: ReactNode - Optional icon
 * - highlighted: boolean - Highlighted variant for important fields
 * - copyable: boolean - Enable copy-to-clipboard
 * - className: string - Additional custom classes
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ConfidenceIndicator from './ConfidenceIndicator';

const FieldDisplay = ({
  label,
  value,
  confidence,
  snippet,
  icon,
  highlighted = false,
  copyable = true,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);
  const [showSnippet, setShowSnippet] = useState(false);

  /**
   * Handle copy to clipboard
   */
  const handleCopy = async () => {
    if (!copyable || !value) return;

    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  /**
   * Base styling
   */
  const baseStyles = `
    relative p-4 rounded-xl border transition-all duration-200
    ${highlighted
      ? 'bg-primary-50 dark:bg-primary-900/10 border-primary-200 dark:border-primary-800'
      : 'bg-background-elevated dark:bg-background-dark-secondary border-border-light dark:border-border-dark'
    }
    ${copyable ? 'cursor-pointer hover:shadow-md hover:border-primary-300 dark:hover:border-primary-700' : ''}
  `;

  return (
    <motion.div
      className={`${baseStyles} ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      onClick={copyable ? handleCopy : undefined}
      onMouseEnter={() => snippet && setShowSnippet(true)}
      onMouseLeave={() => setShowSnippet(false)}
    >
      {/* Icon and Label */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          {/* Icon */}
          {icon && (
            <div
              className={`
                ${highlighted
                  ? 'text-primary-600 dark:text-primary-400'
                  : 'text-neutral-500 dark:text-neutral-400'
                }
              `}
            >
              {icon}
            </div>
          )}

          {/* Label */}
          <span
            className={`
              text-xs font-medium uppercase tracking-wide
              ${highlighted
                ? 'text-primary-700 dark:text-primary-300'
                : 'text-text-tertiary dark:text-text-tertiary'
              }
            `}
          >
            {label}
          </span>
        </div>

        {/* Confidence Indicator */}
        {confidence !== undefined && (
          <ConfidenceIndicator
            value={typeof confidence === 'number' && confidence <= 1 ? confidence * 100 : confidence}
            size="sm"
            variant="badge"
          />
        )}
      </div>

      {/* Value */}
      <div className="flex items-center justify-between gap-2">
        <p
          className={`
            text-base font-semibold truncate
            ${highlighted
              ? 'text-primary-900 dark:text-primary-100'
              : 'text-text-primary dark:text-text-inverse'
            }
          `}
        >
          {value || ''}
        </p>

        {/* Copy Icon */}
        {copyable && value && (
          <motion.div
            className="flex-shrink-0"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <AnimatePresence mode="wait">
              {copied ? (
                <motion.svg
                  key="check"
                  className="w-5 h-5 text-success-DEFAULT"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </motion.svg>
              ) : (
                <motion.svg
                  key="copy"
                  className="w-5 h-5 text-neutral-400 dark:text-neutral-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  initial={{ scale: 1 }}
                  exit={{ scale: 0 }}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </motion.svg>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </div>

      {/* Snippet Tooltip */}
      {snippet && showSnippet && (
        <motion.div
          className="
            absolute top-full left-0 right-0 mt-2 p-3
            bg-neutral-900 dark:bg-neutral-800 text-white
            text-xs rounded-lg shadow-xl z-10
          "
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          transition={{ duration: 0.15 }}
        >
          <p className="font-medium mb-1">Original Text:</p>
          <p className="text-neutral-300 dark:text-neutral-400 italic">
            "{snippet}"
          </p>
          {/* Arrow */}
          <div className="absolute bottom-full left-4">
            <div className="border-4 border-transparent border-b-neutral-900 dark:border-b-neutral-800" />
          </div>
        </motion.div>
      )}

      {/* Copy Success Toast */}
      <AnimatePresence>
        {copied && (
          <motion.div
            className="
              absolute -top-2 -right-2 px-2 py-1
              bg-success-DEFAULT text-white
              text-xs font-medium rounded-md shadow-lg
            "
            initial={{ opacity: 0, scale: 0.8, y: 5 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 5 }}
            transition={{ duration: 0.2 }}
          >
            Copied!
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default FieldDisplay;
