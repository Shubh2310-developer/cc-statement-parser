/**
 * usePolling Hook
 *
 * Custom hook for polling job status until completion.
 * Provides automatic polling with configurable interval and timeout.
 * Integrates with parsingService for status checks.
 *
 * Returns:
 * - jobStatus: Current job status object
 * - isPolling: Boolean indicating if polling is active
 * - error: Error message if polling fails
 * - startPolling: Function to start polling
 * - stopPolling: Function to stop polling
 * - resetPolling: Function to reset state
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { getJobStatus } from '../services/parsingService';

const usePolling = (config = {}) => {
  const {
    interval = 2000, // Default: poll every 2 seconds
    timeout = 300000, // Default: 5 minutes timeout
    onComplete = null, // Callback when job completes
    onError = null, // Callback when job fails
    onProgress = null, // Callback on each status update
  } = config;

  const [jobStatus, setJobStatus] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState(null);

  // Refs for cleanup and timeout tracking
  const pollIntervalRef = useRef(null);
  const timeoutRef = useRef(null);
  const startTimeRef = useRef(null);

  /**
   * Clear all timers and intervals
   */
  const clearTimers = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  /**
   * Stop polling
   */
  const stopPolling = useCallback(() => {
    clearTimers();
    setIsPolling(false);
  }, [clearTimers]);

  /**
   * Poll function - fetch job status
   */
  const poll = useCallback(
    async (jobId) => {
      try {
        // Check if timeout exceeded
        if (startTimeRef.current && Date.now() - startTimeRef.current > timeout) {
          const timeoutError = 'Polling timeout exceeded';
          setError(timeoutError);
          stopPolling();

          if (onError) {
            onError(new Error(timeoutError));
          }
          return;
        }

        // Fetch job status
        const status = await getJobStatus(jobId);
        setJobStatus(status);

        // Call progress callback
        if (onProgress) {
          onProgress(status);
        }

        // Check if job is complete
        if (status.status === 'completed') {
          stopPolling();

          if (onComplete) {
            onComplete(status);
          }
        } else if (status.status === 'failed') {
          const jobError = status.error || 'Job processing failed';
          setError(jobError);
          stopPolling();

          if (onError) {
            onError(new Error(jobError));
          }
        }
      } catch (err) {
        const errorMessage = err.message || 'Failed to fetch job status';
        setError(errorMessage);
        stopPolling();

        if (onError) {
          onError(err);
        }
      }
    },
    [timeout, onProgress, onComplete, onError, stopPolling]
  );

  /**
   * Start polling for a job
   */
  const startPolling = useCallback(
    (jobId) => {
      if (!jobId) {
        setError('Job ID is required');
        return;
      }

      // Clear any existing timers
      clearTimers();

      // Reset state
      setIsPolling(true);
      setError(null);
      setJobStatus(null);
      startTimeRef.current = Date.now();

      // Set timeout for maximum polling duration
      timeoutRef.current = setTimeout(() => {
        const timeoutError = 'Polling timeout exceeded';
        setError(timeoutError);
        stopPolling();

        if (onError) {
          onError(new Error(timeoutError));
        }
      }, timeout);

      // Immediate first poll
      poll(jobId);

      // Set up polling interval
      pollIntervalRef.current = setInterval(() => {
        poll(jobId);
      }, interval);
    },
    [interval, timeout, poll, clearTimers, stopPolling, onError]
  );

  /**
   * Reset polling state
   */
  const resetPolling = useCallback(() => {
    stopPolling();
    setJobStatus(null);
    setError(null);
    startTimeRef.current = null;
  }, [stopPolling]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      clearTimers();
    };
  }, [clearTimers]);

  return {
    jobStatus,
    isPolling,
    error,
    startPolling,
    stopPolling,
    resetPolling,
  };
};

export default usePolling;
