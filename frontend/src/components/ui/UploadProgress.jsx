/**
 * UploadProgress Component
 *
 * Real-time progress feedback during file upload.
 * Features animated progress bar, state indicators, and completion checkmark.
 *
 * Props:
 * - progress: number - Upload progress (0-100)
 * - status: string - Upload status ('uploading' | 'success' | 'error')
 * - fileName: string - Name of file being uploaded
 * - className: string - Additional custom classes
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const UploadProgress = ({
  progress = 0,
  status = 'uploading',
  fileName = '',
  className = '',
}) => {
  /**
   * Color scheme based on status
   */
  const statusColors = {
    uploading: {
      bar: 'bg-primary-500',
      text: 'text-primary-600 dark:text-primary-400',
      background: 'bg-neutral-200 dark:bg-neutral-700',
    },
    success: {
      bar: 'bg-success-DEFAULT',
      text: 'text-success-dark dark:text-success-DEFAULT',
      background: 'bg-neutral-200 dark:bg-neutral-700',
    },
    error: {
      bar: 'bg-error-DEFAULT',
      text: 'text-error-dark dark:text-error-DEFAULT',
      background: 'bg-neutral-200 dark:bg-neutral-700',
    },
  };

  const colors = statusColors[status] || statusColors.uploading;

  /**
   * Status messages
   */
  const statusMessages = {
    uploading: 'Uploading...',
    success: 'Upload complete',
    error: 'Upload failed',
  };

  /**
   * Animation variants for progress bar fill
   */
  const progressBarVariants = {
    initial: { width: 0 },
    animate: {
      width: `${progress}%`,
      transition: {
        duration: 0.3,
        ease: [0.4, 0, 0.2, 1],
      },
    },
  };

  /**
   * Checkmark animation for success state
   */
  const checkmarkVariants = {
    hidden: {
      pathLength: 0,
      opacity: 0,
    },
    visible: {
      pathLength: 1,
      opacity: 1,
      transition: {
        pathLength: {
          duration: 0.5,
          ease: 'easeInOut',
        },
        opacity: {
          duration: 0.2,
        },
      },
    },
  };

  /**
   * Error icon animation
   */
  const errorIconVariants = {
    hidden: {
      scale: 0,
      opacity: 0,
    },
    visible: {
      scale: 1,
      opacity: 1,
      transition: {
        duration: 0.3,
        ease: [0.34, 1.56, 0.64, 1], // Bounce effect
      },
    },
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Progress Bar Container */}
      <div className="relative">
        {/* Background Track */}
        <div
          className={`
            h-2 rounded-full overflow-hidden
            ${colors.background}
          `}
        >
          {/* Animated Progress Fill */}
          <motion.div
            className={`h-full rounded-full ${colors.bar}`}
            variants={progressBarVariants}
            initial="initial"
            animate="animate"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Status Information */}
      <div className="flex items-center justify-between mt-2">
        {/* Status Text with Icon */}
        <div className="flex items-center gap-2">
          <AnimatePresence mode="wait">
            {/* Uploading Spinner */}
            {status === 'uploading' && (
              <motion.div
                key="spinner"
                initial={{ opacity: 0, rotate: 0 }}
                animate={{ opacity: 1, rotate: 360 }}
                exit={{ opacity: 0 }}
                transition={{
                  rotate: {
                    duration: 1,
                    repeat: Infinity,
                    ease: 'linear',
                  },
                }}
                className={`w-4 h-4 border-2 border-t-transparent rounded-full ${colors.text}`}
              />
            )}

            {/* Success Checkmark */}
            {status === 'success' && (
              <motion.svg
                key="checkmark"
                className={`w-5 h-5 ${colors.text}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                initial="hidden"
                animate="visible"
              >
                <motion.path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                  variants={checkmarkVariants}
                />
              </motion.svg>
            )}

            {/* Error Icon */}
            {status === 'error' && (
              <motion.svg
                key="error"
                className={`w-5 h-5 ${colors.text}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                variants={errorIconVariants}
                initial="hidden"
                animate="visible"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </motion.svg>
            )}
          </AnimatePresence>

          {/* Status Message */}
          <motion.p
            className={`text-sm font-medium ${colors.text}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {statusMessages[status]}
          </motion.p>
        </div>

        {/* Progress Percentage */}
        <motion.span
          className={`text-sm font-semibold ${colors.text}`}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          {progress}%
        </motion.span>
      </div>

      {/* Optional: Estimated time remaining (if uploading) */}
      {status === 'uploading' && progress > 0 && progress < 100 && (
        <motion.p
          className="text-xs text-text-tertiary dark:text-text-tertiary mt-1"
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          Processing your file...
        </motion.p>
      )}

      {/* Success Message */}
      {status === 'success' && (
        <motion.p
          className="text-xs text-success-dark dark:text-success-DEFAULT mt-1"
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          {fileName} uploaded successfully
        </motion.p>
      )}

      {/* Error Message */}
      {status === 'error' && (
        <motion.p
          className="text-xs text-error-dark dark:text-error-DEFAULT mt-1"
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          Failed to upload {fileName}. Please try again.
        </motion.p>
      )}
    </div>
  );
};

export default UploadProgress;
