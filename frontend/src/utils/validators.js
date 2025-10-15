/**
 * Validators Utility
 *
 * Client-side validation functions for input sanitization and data integrity.
 * All validators return boolean or error messages for user feedback.
 */

/**
 * Validate file type against accepted types
 *
 * @param {File} file - File object to validate
 * @param {string} acceptedTypes - Comma-separated list of accepted extensions (e.g., '.pdf,.csv')
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidFileType = (file, acceptedTypes = '.pdf') => {
  if (!file) {
    return { isValid: false, error: 'No file provided' };
  }

  // Get file extension
  const fileName = file.name.toLowerCase();
  const fileExtension = '.' + fileName.split('.').pop();

  // Parse accepted types
  const accepted = acceptedTypes
    .split(',')
    .map((type) => type.trim().toLowerCase());

  // Check if extension is in accepted list
  if (!accepted.includes(fileExtension)) {
    return {
      isValid: false,
      error: `File type not supported. Accepted types: ${acceptedTypes}`,
    };
  }

  return { isValid: true, error: null };
};

/**
 * Validate file size against maximum allowed size
 *
 * @param {File} file - File object to validate
 * @param {number} maxMB - Maximum file size in megabytes
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidFileSize = (file, maxMB = 10) => {
  if (!file) {
    return { isValid: false, error: 'No file provided' };
  }

  const maxBytes = maxMB * 1024 * 1024;

  if (file.size > maxBytes) {
    return {
      isValid: false,
      error: `File size exceeds ${maxMB}MB limit`,
    };
  }

  if (file.size === 0) {
    return {
      isValid: false,
      error: 'File is empty',
    };
  }

  return { isValid: true, error: null };
};

/**
 * Validate date string format
 *
 * @param {string} dateString - Date string to validate
 * @param {string} format - Expected format ('iso' | 'any')
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidDate = (dateString, format = 'any') => {
  if (!dateString) {
    return { isValid: false, error: 'Date is required' };
  }

  // Check ISO format (YYYY-MM-DD)
  if (format === 'iso') {
    const isoRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!isoRegex.test(dateString)) {
      return {
        isValid: false,
        error: 'Date must be in YYYY-MM-DD format',
      };
    }
  }

  // Try to parse date
  const date = new Date(dateString);

  if (isNaN(date.getTime())) {
    return {
      isValid: false,
      error: 'Invalid date format',
    };
  }

  // Check if date is in reasonable range (not too far in past/future)
  const year = date.getFullYear();
  if (year < 1900 || year > 2100) {
    return {
      isValid: false,
      error: 'Date must be between 1900 and 2100',
    };
  }

  return { isValid: true, error: null };
};

/**
 * Validate currency amount
 *
 * @param {string|number} amount - Amount to validate
 * @param {Object} options - Validation options
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidCurrency = (amount, options = {}) => {
  const { min = null, max = null, allowNegative = true } = options;

  if (amount === null || amount === undefined || amount === '') {
    return { isValid: false, error: 'Amount is required' };
  }

  // Remove commas and parse
  const cleanAmount = typeof amount === 'string'
    ? amount.replace(/,/g, '')
    : amount;

  const numericAmount = parseFloat(cleanAmount);

  if (isNaN(numericAmount)) {
    return { isValid: false, error: 'Amount must be a valid number' };
  }

  if (!allowNegative && numericAmount < 0) {
    return { isValid: false, error: 'Amount cannot be negative' };
  }

  if (min !== null && numericAmount < min) {
    return {
      isValid: false,
      error: `Amount must be at least ${min}`,
    };
  }

  if (max !== null && numericAmount > max) {
    return {
      isValid: false,
      error: `Amount must not exceed ${max}`,
    };
  }

  return { isValid: true, error: null };
};

/**
 * Sanitize text input to prevent XSS
 *
 * @param {string} text - Text to sanitize
 * @param {Object} options - Sanitization options
 * @returns {string} - Sanitized text
 */
export const sanitizeInput = (text, options = {}) => {
  const { allowHTML = false, maxLength = null } = options;

  if (!text) return '';

  let sanitized = String(text);

  // Remove HTML tags unless explicitly allowed
  if (!allowHTML) {
    sanitized = sanitized.replace(/<[^>]*>/g, '');
  }

  // Escape special characters
  sanitized = sanitized
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');

  // Trim whitespace
  sanitized = sanitized.trim();

  // Apply max length if specified
  if (maxLength && sanitized.length > maxLength) {
    sanitized = sanitized.slice(0, maxLength);
  }

  return sanitized;
};

/**
 * Validate email format
 *
 * @param {string} email - Email address to validate
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidEmail = (email) => {
  if (!email) {
    return { isValid: false, error: 'Email is required' };
  }

  // RFC 5322 simplified regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Invalid email format' };
  }

  return { isValid: true, error: null };
};

/**
 * Validate card last 4 digits
 *
 * @param {string} last4 - Last 4 digits to validate
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidCardLast4 = (last4) => {
  if (!last4) {
    return { isValid: false, error: 'Card number is required' };
  }

  const cleaned = String(last4).replace(/\D/g, '');

  if (cleaned.length !== 4) {
    return {
      isValid: false,
      error: 'Card number must be 4 digits',
    };
  }

  return { isValid: true, error: null };
};

/**
 * Validate confidence score (0-100 or 0-1)
 *
 * @param {number} confidence - Confidence score
 * @param {boolean} normalized - If true, expects 0-1 range
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidConfidence = (confidence, normalized = false) => {
  if (confidence === null || confidence === undefined) {
    return { isValid: false, error: 'Confidence is required' };
  }

  const numericConfidence = Number(confidence);

  if (isNaN(numericConfidence)) {
    return { isValid: false, error: 'Confidence must be a number' };
  }

  const min = 0;
  const max = normalized ? 1 : 100;

  if (numericConfidence < min || numericConfidence > max) {
    return {
      isValid: false,
      error: `Confidence must be between ${min} and ${max}`,
    };
  }

  return { isValid: true, error: null };
};

/**
 * Validate job ID format
 *
 * @param {string} jobId - Job ID to validate
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidJobId = (jobId) => {
  if (!jobId) {
    return { isValid: false, error: 'Job ID is required' };
  }

  // Accept UUID or alphanumeric strings
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  const alphanumericRegex = /^[a-zA-Z0-9_-]{8,64}$/;

  if (!uuidRegex.test(jobId) && !alphanumericRegex.test(jobId)) {
    return { isValid: false, error: 'Invalid job ID format' };
  }

  return { isValid: true, error: null };
};

/**
 * Validate URL format
 *
 * @param {string} url - URL to validate
 * @returns {Object} - { isValid: boolean, error: string|null }
 */
export const isValidURL = (url) => {
  if (!url) {
    return { isValid: false, error: 'URL is required' };
  }

  try {
    new URL(url);
    return { isValid: true, error: null };
  } catch {
    return { isValid: false, error: 'Invalid URL format' };
  }
};

/**
 * Batch validator - runs multiple validators on same value
 *
 * @param {any} value - Value to validate
 * @param {Array<Function>} validators - Array of validator functions
 * @returns {Object} - { isValid: boolean, errors: Array<string> }
 */
export const validateBatch = (value, validators) => {
  const errors = [];

  for (const validator of validators) {
    const result = validator(value);
    if (!result.isValid) {
      errors.push(result.error);
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate form data object
 *
 * @param {Object} data - Form data to validate
 * @param {Object} schema - Validation schema
 * @returns {Object} - { isValid: boolean, errors: Object }
 */
export const validateForm = (data, schema) => {
  const errors = {};
  let isValid = true;

  for (const [field, validator] of Object.entries(schema)) {
    const value = data[field];
    const result = validator(value);

    if (!result.isValid) {
      errors[field] = result.error;
      isValid = false;
    }
  }

  return { isValid, errors };
};

export default {
  isValidFileType,
  isValidFileSize,
  isValidDate,
  isValidCurrency,
  sanitizeInput,
  isValidEmail,
  isValidCardLast4,
  isValidConfidence,
  isValidJobId,
  isValidURL,
  validateBatch,
  validateForm,
};
