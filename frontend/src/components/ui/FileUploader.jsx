/**
 * FileUploader Component
 *
 * Professional file upload interface with drag-and-drop support.
 * Features elegant animations, validation, and state management.
 *
 * Props:
 * - onFileSelect: Function - Callback when file is selected
 * - acceptedTypes: string - Accepted file types (e.g., '.pdf,.csv')
 * - maxSizeMB: number - Maximum file size in megabytes (default: 10)
 * - className: string - Additional custom classes
 */

import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Button from './Button';
import UploadProgress from './UploadProgress';
import useFileUpload from '../../hooks/useFileUpload';

const FileUploader = ({
  onFileSelect,
  acceptedTypes = '.pdf,.csv,.xlsx,.xls',
  maxSizeMB = 10,
  className = '',
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const fileInputRef = useRef(null);

  // Use file upload hook for state management
  const {
    file,
    progress,
    status,
    error: uploadError,
    uploadFile,
    cancelUpload,
    resetUpload,
  } = useFileUpload('/api/upload');

  /**
   * Validate file type and size
   */
  const validateFile = useCallback(
    (fileToValidate) => {
      // Check file size
      const maxSizeBytes = maxSizeMB * 1024 * 1024;
      if (fileToValidate.size > maxSizeBytes) {
        setValidationError(`File size must be less than ${maxSizeMB}MB`);
        return false;
      }

      // Check file type
      if (acceptedTypes) {
        const fileExtension = '.' + fileToValidate.name.split('.').pop().toLowerCase();
        const acceptedExtensions = acceptedTypes.split(',').map((type) => type.trim());

        if (!acceptedExtensions.includes(fileExtension)) {
          setValidationError(`File type not supported. Accepted types: ${acceptedTypes}`);
          return false;
        }
      }

      setValidationError(null);
      return true;
    },
    [acceptedTypes, maxSizeMB]
  );

  /**
   * Handle file selection
   */
  const handleFileSelect = useCallback(
    (selectedFile) => {
      if (validateFile(selectedFile)) {
        // Upload file
        uploadFile(selectedFile);

        // Notify parent component
        if (onFileSelect) {
          onFileSelect(selectedFile);
        }
      }
    },
    [validateFile, uploadFile, onFileSelect]
  );

  /**
   * Handle drag events
   */
  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const droppedFiles = e.dataTransfer.files;
      if (droppedFiles.length > 0) {
        handleFileSelect(droppedFiles[0]);
      }
    },
    [handleFileSelect]
  );

  /**
   * Handle file input change
   */
  const handleInputChange = useCallback(
    (e) => {
      const selectedFiles = e.target.files;
      if (selectedFiles.length > 0) {
        handleFileSelect(selectedFiles[0]);
      }
    },
    [handleFileSelect]
  );

  /**
   * Trigger file input click
   */
  const handleBrowseClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  /**
   * Handle upload reset
   */
  const handleReset = useCallback(() => {
    resetUpload();
    setValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [resetUpload]);

  /**
   * Format file size for display
   */
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  /**
   * Animation variants
   */
  const dropZoneVariants = {
    idle: {
      borderColor: 'rgb(203, 213, 225)', // border-default
      backgroundColor: 'transparent',
    },
    dragging: {
      borderColor: 'rgb(20, 184, 166)', // primary-500
      backgroundColor: 'rgba(20, 184, 166, 0.05)',
      scale: 1.01,
      transition: {
        duration: 0.2,
      },
    },
  };

  const errorDisplay = validationError || uploadError;

  return (
    <div className={`w-full ${className}`}>
      {/* Drag and Drop Zone */}
      <motion.div
        className={`
          relative border-2 border-dashed rounded-2xl p-8
          transition-all duration-300
          ${isDragging ? 'border-primary-500' : 'border-border-default dark:border-border-dark'}
          ${status === 'idle' ? 'cursor-pointer' : 'cursor-default'}
        `}
        variants={dropZoneVariants}
        animate={isDragging ? 'dragging' : 'idle'}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={status === 'idle' ? handleBrowseClick : undefined}
      >
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedTypes}
          onChange={handleInputChange}
          className="hidden"
          aria-label="File upload input"
        />

        {/* Upload Icon and Text */}
        <AnimatePresence mode="wait">
          {status === 'idle' && !file && (
            <motion.div
              key="idle"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center justify-center text-center"
            >
              {/* Upload Icon */}
              <motion.div
                className="mb-4 p-4 rounded-full bg-neutral-100 dark:bg-neutral-800"
                animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
                transition={{ duration: 0.2 }}
              >
                <svg
                  className="w-8 h-8 text-neutral-400 dark:text-neutral-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </motion.div>

              {/* Instructions */}
              <h3 className="text-lg font-semibold text-text-primary dark:text-text-inverse mb-2">
                {isDragging ? 'Drop file here' : 'Upload your file'}
              </h3>
              <p className="text-sm text-text-secondary dark:text-text-tertiary mb-4">
                Drag and drop or click to browse
              </p>

              {/* Browse Button */}
              <Button variant="outline" size="md" onClick={handleBrowseClick}>
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
                  />
                </svg>
                Browse Files
              </Button>

              {/* File Type Info */}
              <p className="text-xs text-text-tertiary dark:text-text-tertiary mt-4">
                Accepted formats: {acceptedTypes.replace(/\./g, '').toUpperCase()} • Max size: {maxSizeMB}MB
              </p>
            </motion.div>
          )}

          {/* File Selected Info */}
          {file && status !== 'idle' && (
            <motion.div
              key="file-info"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              {/* File Details */}
              <div className="flex items-center gap-3">
                {/* File Icon */}
                <div className="flex-shrink-0 p-3 rounded-lg bg-primary-50 dark:bg-primary-900/20">
                  <svg
                    className="w-6 h-6 text-primary-600 dark:text-primary-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>

                {/* File Name and Size */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary dark:text-text-inverse truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-text-tertiary dark:text-text-tertiary">
                    {formatFileSize(file.size)}
                  </p>
                </div>

                {/* Action Buttons */}
                {status === 'uploading' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={cancelUpload}
                    className="flex-shrink-0"
                  >
                    Cancel
                  </Button>
                )}

                {(status === 'success' || status === 'error') && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleReset}
                    className="flex-shrink-0"
                  >
                    Remove
                  </Button>
                )}
              </div>

              {/* Upload Progress */}
              <UploadProgress
                progress={progress}
                status={status}
                fileName={file.name}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Validation/Upload Error Message */}
      <AnimatePresence>
        {errorDisplay && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-3 flex items-start gap-2 text-sm text-error-dark dark:text-error-DEFAULT"
          >
            <svg
              className="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{errorDisplay}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FileUploader;
