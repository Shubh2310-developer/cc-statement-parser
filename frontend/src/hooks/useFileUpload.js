/**
 * useFileUpload Hook
 *
 * Custom hook for handling file upload logic and progress tracking.
 * Integrates with parsingService for credit card statement processing.
 *
 * Returns:
 * - file: Current file object
 * - progress: Upload progress (0-100)
 * - status: 'idle' | 'uploading' | 'success' | 'error'
 * - error: Error message if upload fails
 * - jobId: Job identifier returned after successful upload
 * - uploadFile: Function to initiate upload
 * - cancelUpload: Function to abort upload
 * - resetUpload: Function to reset state
 */

import { useState, useRef, useCallback } from 'react';
import { uploadFile as uploadFileService } from '../services/parsingService';

const useFileUpload = (options = {}) => {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle'); // 'idle' | 'uploading' | 'success' | 'error'
  const [error, setError] = useState(null);
  const [jobId, setJobId] = useState(null);

  // Reference to cancel token (if needed for cancellation)
  const cancelTokenRef = useRef(null);

  /**
   * Upload file to server with progress tracking
   */
  const uploadFile = useCallback(
    async (fileToUpload, uploadOptions = {}) => {
      if (!fileToUpload) {
        setError('No file selected');
        setStatus('error');
        return null;
      }

      try {
        // Reset state
        setFile(fileToUpload);
        setProgress(0);
        setStatus('uploading');
        setError(null);
        setJobId(null);

        // Progress callback
        const handleProgress = (percent) => {
          setProgress(percent);
        };

        // Merge options
        const mergedOptions = { ...options, ...uploadOptions };

        // Call parsing service
        const result = await uploadFileService(
          fileToUpload,
          mergedOptions,
          handleProgress
        );

        // Update state on success
        setStatus('success');
        setProgress(100);
        setJobId(result.jobId);

        return result;
      } catch (err) {
        // Handle upload error
        const errorMessage = err.message || 'Upload failed';
        setStatus('error');
        setError(errorMessage);
        setProgress(0);

        throw err;
      }
    },
    [options]
  );

  /**
   * Cancel ongoing upload
   * Note: Axios-based uploads can be cancelled using cancel tokens
   * For now, this is a placeholder for future implementation
   */
  const cancelUpload = useCallback(() => {
    if (cancelTokenRef.current) {
      cancelTokenRef.current.cancel('Upload cancelled by user');
      cancelTokenRef.current = null;
    }

    // Reset to idle state
    setStatus('idle');
    setProgress(0);
    setError('Upload cancelled');
  }, []);

  /**
   * Reset upload state
   */
  const resetUpload = useCallback(() => {
    setFile(null);
    setProgress(0);
    setStatus('idle');
    setError(null);
    setJobId(null);
    cancelTokenRef.current = null;
  }, []);

  return {
    file,
    progress,
    status,
    error,
    jobId,
    uploadFile,
    cancelUpload,
    resetUpload,
  };
};

export default useFileUpload;
