/**
 * Parsing Service
 *
 * Encapsulates all credit card statement parsing API endpoints.
 * Provides clean, promise-based interface for:
 * - File upload and parsing initiation
 * - Job status polling
 * - Result retrieval
 *
 * All responses are normalized for consistent handling.
 */

import api, { withRetry, getErrorMessage } from './api';

const IS_DEV = import.meta.env.DEV;

/**
 * Upload file for parsing
 *
 * @param {File} file - File object to upload
 * @param {Object} options - Additional parsing options
 * @param {Function} onProgress - Progress callback (percent: number) => void
 * @returns {Promise<Object>} - { jobId, status, message }
 */
export const uploadFile = async (file, options = {}, onProgress = null) => {
  try {
    if (!file) {
      throw new Error('File is required');
    }

    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('file', file);

    // Append additional options if provided
    if (options.extractMetadata !== undefined) {
      formData.append('extract_metadata', options.extractMetadata);
    }
    if (options.validateTransactions !== undefined) {
      formData.append('validate_transactions', options.validateTransactions);
    }

    if (IS_DEV) {
      console.log('[Parsing Service] Uploading file:', {
        name: file.name,
        size: file.size,
        type: file.type,
        options,
      });
    }

    // Send upload request with progress tracking
    const response = await api.post('/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    // Normalize response
    const result = {
      jobId: response.data.job_id || response.data.jobId,
      status: response.data.status,
      message: response.data.message || 'File uploaded successfully',
      timestamp: response.data.timestamp || new Date().toISOString(),
    };

    if (IS_DEV) {
      console.log('[Parsing Service] Upload successful:', result);
    }

    return result;
  } catch (error) {
    const errorMessage = getErrorMessage(error);

    if (IS_DEV) {
      console.error('[Parsing Service] Upload failed:', errorMessage);
    }

    throw new Error(`Upload failed: ${errorMessage}`);
  }
};

/**
 * Get job status
 *
 * @param {string} jobId - Job identifier
 * @returns {Promise<Object>} - { jobId, status, progress, message, completedAt }
 */
export const getJobStatus = async (jobId) => {
  try {
    if (!jobId) {
      throw new Error('Job ID is required');
    }

    if (IS_DEV) {
      console.log('[Parsing Service] Fetching job status:', jobId);
    }

    // Use retry wrapper for polling reliability
    const response = await withRetry(
      () => api.get(`/jobs/${jobId}`),
      2, // Max 2 retries for status checks
      500 // 500ms base delay
    );

    // Normalize response
    const result = {
      jobId: response.data.job_id || response.data.jobId || jobId,
      status: response.data.status, // 'pending' | 'processing' | 'completed' | 'failed'
      progress: response.data.progress || 0, // 0-100
      message: response.data.message,
      error: response.data.error,
      createdAt: response.data.created_at || response.data.createdAt,
      completedAt: response.data.completed_at || response.data.completedAt,
    };

    if (IS_DEV) {
      console.log('[Parsing Service] Job status:', result);
    }

    return result;
  } catch (error) {
    const errorMessage = getErrorMessage(error);

    if (IS_DEV) {
      console.error('[Parsing Service] Failed to fetch job status:', errorMessage);
    }

    throw new Error(`Failed to get job status: ${errorMessage}`);
  }
};

/**
 * Get parsing results
 *
 * @param {string} jobId - Job identifier
 * @returns {Promise<Object>} - { jobId, data, metadata, summary }
 */
export const getResults = async (jobId) => {
  try {
    if (!jobId) {
      throw new Error('Job ID is required');
    }

    if (IS_DEV) {
      console.log('[Parsing Service] Fetching results for job:', jobId);
    }

    const response = await api.get(`/results/${jobId}`);

    // Normalize response
    const result = {
      jobId: response.data.job_id || response.data.jobId || jobId,
      data: response.data.data || response.data.results || [],
      metadata: response.data.metadata || {},
      summary: response.data.summary || {},
      fileName: response.data.file_name || response.data.fileName,
      processedAt: response.data.processed_at || response.data.processedAt,
    };

    if (IS_DEV) {
      console.log('[Parsing Service] Results retrieved:', {
        jobId: result.jobId,
        recordCount: result.data?.length || 0,
        fileName: result.fileName,
      });
    }

    return result;
  } catch (error) {
    const errorMessage = getErrorMessage(error);

    if (IS_DEV) {
      console.error('[Parsing Service] Failed to fetch results:', errorMessage);
    }

    throw new Error(`Failed to get results: ${errorMessage}`);
  }
};

/**
 * Poll job status until completion
 *
 * @param {string} jobId - Job identifier
 * @param {Object} options - Polling configuration
 * @param {number} options.interval - Polling interval in ms (default: 2000)
 * @param {number} options.timeout - Max polling duration in ms (default: 300000 = 5min)
 * @param {Function} options.onProgress - Progress callback (status: Object) => void
 * @returns {Promise<Object>} - Final job status
 */
export const pollJobStatus = async (
  jobId,
  { interval = 2000, timeout = 300000, onProgress = null } = {}
) => {
  const startTime = Date.now();

  if (IS_DEV) {
    console.log('[Parsing Service] Starting job polling:', {
      jobId,
      interval,
      timeout,
    });
  }

  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        // Check timeout
        if (Date.now() - startTime > timeout) {
          clearInterval(pollInterval);
          reject(new Error('Job polling timeout exceeded'));
          return;
        }

        // Fetch job status
        const status = await getJobStatus(jobId);

        // Call progress callback if provided
        if (onProgress) {
          onProgress(status);
        }

        // Check if job is complete
        if (status.status === 'completed') {
          clearInterval(pollInterval);
          resolve(status);
        } else if (status.status === 'failed') {
          clearInterval(pollInterval);
          reject(new Error(status.error || 'Job processing failed'));
        }
      } catch (error) {
        clearInterval(pollInterval);
        reject(error);
      }
    };

    // Start polling
    const pollInterval = setInterval(poll, interval);

    // Initial poll
    poll();
  });
};

/**
 * Cancel a job
 *
 * @param {string} jobId - Job identifier
 * @returns {Promise<Object>} - { jobId, status, message }
 */
export const cancelJob = async (jobId) => {
  try {
    if (!jobId) {
      throw new Error('Job ID is required');
    }

    if (IS_DEV) {
      console.log('[Parsing Service] Cancelling job:', jobId);
    }

    const response = await api.delete(`/jobs/${jobId}`);

    const result = {
      jobId: response.data.job_id || response.data.jobId || jobId,
      status: response.data.status,
      message: response.data.message || 'Job cancelled successfully',
    };

    if (IS_DEV) {
      console.log('[Parsing Service] Job cancelled:', result);
    }

    return result;
  } catch (error) {
    const errorMessage = getErrorMessage(error);

    if (IS_DEV) {
      console.error('[Parsing Service] Failed to cancel job:', errorMessage);
    }

    throw new Error(`Failed to cancel job: ${errorMessage}`);
  }
};

/**
 * Download results as file
 *
 * @param {string} jobId - Job identifier
 * @param {string} format - Export format ('csv' | 'json' | 'xlsx')
 * @returns {Promise<Blob>} - File blob
 */
export const downloadResults = async (jobId, format = 'csv') => {
  try {
    if (!jobId) {
      throw new Error('Job ID is required');
    }

    if (IS_DEV) {
      console.log('[Parsing Service] Downloading results:', { jobId, format });
    }

    const response = await api.get(`/results/${jobId}/download`, {
      params: { format },
      responseType: 'blob',
    });

    if (IS_DEV) {
      console.log('[Parsing Service] Download successful');
    }

    return response.data;
  } catch (error) {
    const errorMessage = getErrorMessage(error);

    if (IS_DEV) {
      console.error('[Parsing Service] Download failed:', errorMessage);
    }

    throw new Error(`Failed to download results: ${errorMessage}`);
  }
};

/**
 * Export all service functions
 */
export default {
  uploadFile,
  getJobStatus,
  getResults,
  pollJobStatus,
  cancelJob,
  downloadResults,
};
