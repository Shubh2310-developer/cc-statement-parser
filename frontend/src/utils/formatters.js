/**
 * Formatters Utility
 *
 * Professional data formatting functions for display consistency.
 * All formatters handle edge cases and return user-friendly strings.
 */

/**
 * Format currency amount with symbol and proper separators
 *
 * @param {number|string} amount - Amount to format
 * @param {string} currency - Currency code (default: 'INR')
 * @param {Object} options - Formatting options
 * @returns {string} - Formatted currency string
 */
export const formatCurrency = (amount, currency = 'INR', options = {}) => {
  const {
    showSymbol = true,
    decimals = 2,
    locale = 'en-IN',
  } = options;

  // Handle invalid inputs
  if (amount === null || amount === undefined || amount === '') {
    return '';
  }

  const numericAmount = typeof amount === 'string'
    ? parseFloat(amount.replace(/,/g, ''))
    : amount;

  if (isNaN(numericAmount)) {
    return '';
  }

  const formatter = new Intl.NumberFormat(locale, {
    style: showSymbol ? 'currency' : 'decimal',
    currency: currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return formatter.format(numericAmount);
};

/**
 * Format date string with various output formats
 *
 * @param {string|Date} date - Date to format
 * @param {string} format - Output format ('short' | 'medium' | 'long' | 'iso')
 * @returns {string} - Formatted date string
 */
export const formatDate = (date, format = 'medium') => {
  if (!date) return '';

  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  const formats = {
    short: { month: '2-digit', day: '2-digit', year: 'numeric' }, // 09/15/2025
    medium: { month: 'short', day: '2-digit', year: 'numeric' },  // Sep 15, 2025
    long: { month: 'long', day: '2-digit', year: 'numeric' },     // September 15, 2025
    iso: null, // Return ISO string
  };

  if (format === 'iso') {
    return dateObj.toISOString().split('T')[0]; // 2025-09-15
  }

  const formatter = new Intl.DateTimeFormat('en-IN', formats[format] || formats.medium);
  return formatter.format(dateObj);
};

/**
 * Format card number with masking
 *
 * @param {string} last4 - Last 4 digits of card
 * @param {boolean} showMask - Show bullet points before digits
 * @returns {string} - Formatted card number
 */
export const formatCardNumber = (last4, showMask = true) => {
  if (!last4) return '';

  const digits = String(last4).slice(-4);

  if (showMask) {
    return `"""" ${digits}`;
  }

  return digits;
};

/**
 * Format percentage value
 *
 * @param {number} value - Value to format (0-100 or 0-1)
 * @param {Object} options - Formatting options
 * @returns {string} - Formatted percentage string
 */
export const formatPercentage = (value, options = {}) => {
  const {
    decimals = 0,
    normalize = false, // If true, multiply by 100 (for 0-1 range)
  } = options;

  if (value === null || value === undefined) {
    return '';
  }

  const numericValue = typeof value === 'string' ? parseFloat(value) : value;

  if (isNaN(numericValue)) {
    return '';
  }

  const percentValue = normalize ? numericValue * 100 : numericValue;

  return `${percentValue.toFixed(decimals)}%`;
};

/**
 * Format file size in human-readable format
 *
 * @param {number} bytes - Size in bytes
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted file size
 */
export const formatFileSize = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  if (!bytes || bytes < 0) return '';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  const size = bytes / Math.pow(k, i);
  return `${size.toFixed(decimals)} ${sizes[i]}`;
};

/**
 * Truncate text with ellipsis
 *
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @param {string} suffix - Suffix to add (default: '...')
 * @returns {string} - Truncated text
 */
export const truncateText = (text, maxLength = 50, suffix = '...') => {
  if (!text) return '';
  if (text.length <= maxLength) return text;

  return text.slice(0, maxLength - suffix.length) + suffix;
};

/**
 * Format transaction amount with color indication
 *
 * @param {number} amount - Transaction amount
 * @param {string} currency - Currency code
 * @returns {Object} - { formatted, isCredit, color }
 */
export const formatTransactionAmount = (amount, currency = 'INR') => {
  const isCredit = amount > 0;
  const formatted = formatCurrency(Math.abs(amount), currency);

  return {
    formatted: isCredit ? `+${formatted}` : `-${formatted}`,
    isCredit,
    color: isCredit
      ? 'text-success-dark dark:text-success-DEFAULT'
      : 'text-text-primary dark:text-text-inverse',
  };
};

/**
 * Format relative time (e.g., "2 hours ago")
 *
 * @param {string|Date} date - Date to compare
 * @returns {string} - Relative time string
 */
export const formatRelativeTime = (date) => {
  if (!date) return '';

  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now - dateObj;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return 'Just now';
  if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
  if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
  if (diffDay < 30) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;

  return formatDate(dateObj, 'medium');
};

/**
 * Format confidence score with status
 *
 * @param {number} confidence - Confidence value (0-1 or 0-100)
 * @param {boolean} normalize - If true, expects 0-1 range
 * @returns {Object} - { percentage, status, color }
 */
export const formatConfidence = (confidence, normalize = false) => {
  if (confidence === null || confidence === undefined) {
    return {
      percentage: '',
      status: 'unknown',
      color: 'text-neutral-500',
    };
  }

  const value = normalize ? confidence * 100 : confidence;

  let status = 'low';
  let color = 'text-error-dark dark:text-error-DEFAULT';

  if (value >= 90) {
    status = 'high';
    color = 'text-success-dark dark:text-success-DEFAULT';
  } else if (value >= 70) {
    status = 'medium';
    color = 'text-warning-dark dark:text-warning-DEFAULT';
  }

  return {
    percentage: `${Math.round(value)}%`,
    status,
    color,
  };
};

/**
 * Format job status for display
 *
 * @param {string} status - Job status
 * @returns {Object} - { label, color, icon }
 */
export const formatJobStatus = (status) => {
  const statusMap = {
    pending: {
      label: 'Pending',
      color: 'text-neutral-600 dark:text-neutral-400',
      bgColor: 'bg-neutral-100 dark:bg-neutral-800',
    },
    processing: {
      label: 'Processing',
      color: 'text-primary-600 dark:text-primary-400',
      bgColor: 'bg-primary-100 dark:bg-primary-900/20',
    },
    completed: {
      label: 'Completed',
      color: 'text-success-dark dark:text-success-DEFAULT',
      bgColor: 'bg-success-light dark:bg-success-dark/20',
    },
    failed: {
      label: 'Failed',
      color: 'text-error-dark dark:text-error-DEFAULT',
      bgColor: 'bg-error-light dark:bg-error-dark/20',
    },
  };

  return statusMap[status] || statusMap.pending;
};

/**
 * Capitalize first letter of string
 *
 * @param {string} text - Text to capitalize
 * @returns {string} - Capitalized text
 */
export const capitalize = (text) => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

/**
 * Format issuer name for display
 *
 * @param {string} issuer - Issuer code
 * @returns {string} - Formatted issuer name
 */
export const formatIssuer = (issuer) => {
  const issuerMap = {
    HDFC: 'HDFC Bank',
    ICICI: 'ICICI Bank',
    SBI: 'SBI Card',
    AXIS: 'Axis Bank',
    AMEX: 'American Express',
  };

  return issuerMap[issuer?.toUpperCase()] || issuer || 'Unknown';
};

export default {
  formatCurrency,
  formatDate,
  formatCardNumber,
  formatPercentage,
  formatFileSize,
  truncateText,
  formatTransactionAmount,
  formatRelativeTime,
  formatConfidence,
  formatJobStatus,
  capitalize,
  formatIssuer,
};
