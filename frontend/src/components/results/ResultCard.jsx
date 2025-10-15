/**
 * ResultCard Component
 *
 * Professional display container for parsed credit card statement results.
 * Shows extracted fields, confidence scores, and metadata with refined styling.
 *
 * Props:
 * - data: Object - Parsed statement data
 * - issuer: string - Credit card issuer name
 * - jobId: string - Job identifier
 * - onViewPDF: Function - Callback to view PDF with highlights
 * - className: string - Additional custom classes
 */

import React from 'react';
import { motion } from 'framer-motion';
import Card from '../ui/Card';
import FieldDisplay from './FieldDisplay';
import TransactionTable from './TransactionTable';
import ConfidenceIndicator from './ConfidenceIndicator';
import Button from '../ui/Button';

const ResultCard = ({
  data,
  issuer = 'Unknown',
  jobId,
  onViewPDF,
  className = '',
}) => {
  if (!data || !data.fields) {
    return (
      <Card className={className} variant="bordered">
        <div className="text-center py-8">
          <p className="text-text-tertiary dark:text-text-tertiary">
            No results available
          </p>
        </div>
      </Card>
    );
  }

  const { fields, status, raw_text_snippets } = data;

  /**
   * Calculate overall confidence score
   */
  const calculateOverallConfidence = () => {
    const confidenceValues = Object.values(fields)
      .filter((field) => field?.confidence !== undefined)
      .map((field) => field.confidence);

    if (confidenceValues.length === 0) return 0;

    const average =
      confidenceValues.reduce((sum, val) => sum + val, 0) /
      confidenceValues.length;

    return Math.round(average * 100);
  };

  const overallConfidence = calculateOverallConfidence();

  /**
   * Issuer badge styling
   */
  const issuerStyles = {
    HDFC: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800',
    ICICI:
      'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-800',
    SBI: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800',
    AXIS: 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400 dark:border-purple-800',
    AMEX: 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-900/20 dark:text-slate-400 dark:border-slate-800',
    default:
      'bg-neutral-50 text-neutral-700 border-neutral-200 dark:bg-neutral-900/20 dark:text-neutral-400 dark:border-neutral-800',
  };

  const issuerStyle = issuerStyles[issuer.toUpperCase()] || issuerStyles.default;

  return (
    <Card
      className={`${className}`}
      variant="elevated"
      padding="lg"
      hoverable={false}
    >
      {/* Header Section */}
      <div className="flex items-start justify-between mb-6 pb-6 border-b border-border-light dark:border-border-dark">
        <div className="flex-1">
          {/* Issuer Badge */}
          <div className="flex items-center gap-3 mb-3">
            <span
              className={`px-3 py-1 text-sm font-semibold rounded-lg border ${issuerStyle}`}
            >
              {issuer}
            </span>
            <ConfidenceIndicator value={overallConfidence} size="sm" />
          </div>

          {/* Job ID */}
          <p className="text-xs text-text-tertiary dark:text-text-tertiary font-mono">
            Job ID: {jobId}
          </p>
        </div>

        {/* View PDF Button */}
        {onViewPDF && (
          <Button
            variant="outline"
            size="sm"
            onClick={onViewPDF}
            leftIcon={
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
            }
          >
            View PDF
          </Button>
        )}
      </div>

      {/* Extracted Fields Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Card Last 4 Digits */}
        {fields.card_last4 && (
          <FieldDisplay
            label="Card Number"
            value={fields.card_last4.value}
            confidence={fields.card_last4.confidence}
            snippet={fields.card_last4.snippet}
            icon={
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
                  d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                />
              </svg>
            }
          />
        )}

        {/* Card Variant */}
        {fields.card_variant && (
          <FieldDisplay
            label="Card Variant"
            value={fields.card_variant.value}
            confidence={fields.card_variant.confidence}
            snippet={fields.card_variant.snippet}
            icon={
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
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            }
          />
        )}

        {/* Billing Cycle */}
        {fields.billing_cycle && (
          <FieldDisplay
            label="Billing Cycle"
            value={`${fields.billing_cycle.start} to ${fields.billing_cycle.end}`}
            confidence={fields.billing_cycle.confidence}
            snippet={fields.billing_cycle.snippet}
            icon={
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
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            }
          />
        )}

        {/* Payment Due Date */}
        {fields.due_date && (
          <FieldDisplay
            label="Payment Due Date"
            value={fields.due_date.value}
            confidence={fields.due_date.confidence}
            snippet={fields.due_date.snippet}
            highlighted
            icon={
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
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            }
          />
        )}
      </div>

      {/* Transaction Table */}
      {fields.transactions && fields.transactions.rows && (
        <div className="mt-6 pt-6 border-t border-border-light dark:border-border-dark">
          <TransactionTable
            transactions={fields.transactions.rows}
            confidence={fields.transactions.confidence}
          />
        </div>
      )}

      {/* Status Badge */}
      {status && (
        <motion.div
          className="mt-4 flex items-center gap-2 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="w-2 h-2 rounded-full bg-success-DEFAULT" />
          <span className="text-text-tertiary dark:text-text-tertiary">
            Status: <span className="text-text-secondary dark:text-text-secondary font-medium">{status}</span>
          </span>
        </motion.div>
      )}
    </Card>
  );
};

export default ResultCard;
