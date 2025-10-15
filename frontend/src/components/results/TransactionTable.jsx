/**
 * TransactionTable Component
 *
 * Professional transaction data table with sorting, filtering, and export.
 * Responsive design with card view on mobile.
 *
 * Props:
 * - transactions: Array - Transaction data
 * - confidence: number - Overall table confidence score
 * - pageSize: number - Number of rows per page
 * - showExport: boolean - Show export button
 * - className: string - Additional custom classes
 */

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { formatDate, formatTransactionAmount, formatCurrency } from '../../utils/formatters';
import ConfidenceIndicator from './ConfidenceIndicator';
import Button from '../ui/Button';

const TransactionTable = ({
  transactions = [],
  confidence,
  pageSize = 10,
  showExport = true,
  className = '',
}) => {
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');

  /**
   * Filter and sort transactions
   */
  const processedTransactions = useMemo(() => {
    let filtered = [...transactions];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter((tx) =>
        tx.desc?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tx.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Sort transactions
    filtered.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];

      // Handle date sorting
      if (sortField === 'date') {
        aValue = new Date(aValue || a.transaction_date);
        bValue = new Date(bValue || b.transaction_date);
      }

      // Handle amount sorting
      if (sortField === 'amount') {
        aValue = parseFloat(aValue || 0);
        bValue = parseFloat(bValue || 0);
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [transactions, sortField, sortDirection, searchTerm]);

  /**
   * Pagination
   */
  const totalPages = Math.ceil(processedTransactions.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedTransactions = processedTransactions.slice(startIndex, endIndex);

  /**
   * Handle sort
   */
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  /**
   * Handle export
   */
  const handleExport = (format = 'csv') => {
    if (format === 'csv') {
      const headers = ['Date', 'Description', 'Amount'];
      const rows = processedTransactions.map((tx) => [
        tx.date || tx.transaction_date,
        tx.desc || tx.description,
        tx.amount,
      ]);

      const csvContent = [
        headers.join(','),
        ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    }
  };

  /**
   * Sort icon
   */
  const SortIcon = ({ field }) => {
    if (sortField !== field) {
      return (
        <svg className="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }

    return sortDirection === 'asc' ? (
      <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  if (!transactions || transactions.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-text-tertiary dark:text-text-tertiary">
          No transactions found
        </p>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-text-primary dark:text-text-inverse">
            Transactions ({processedTransactions.length})
          </h3>
          {confidence !== undefined && (
            <ConfidenceIndicator value={typeof confidence === 'number' && confidence <= 1 ? confidence * 100 : confidence} size="sm" />
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="
                pl-9 pr-3 py-1.5 text-sm
                border border-border-light dark:border-border-dark
                rounded-lg bg-background-elevated dark:bg-background-dark
                text-text-primary dark:text-text-inverse
                focus:outline-none focus:ring-2 focus:ring-primary-500
                transition-all duration-200
              "
            />
            <svg
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          {/* Export Button */}
          {showExport && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport('csv')}
              leftIcon={
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              }
            >
              Export
            </Button>
          )}
        </div>
      </div>

      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto rounded-xl border border-border-light dark:border-border-dark">
        <table className="w-full">
          <thead className="bg-neutral-50 dark:bg-neutral-900/50">
            <tr>
              <th
                className="px-4 py-3 text-left text-xs font-semibold text-text-tertiary dark:text-text-tertiary uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                onClick={() => handleSort('date')}
              >
                <div className="flex items-center gap-1">
                  Date
                  <SortIcon field="date" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-left text-xs font-semibold text-text-tertiary dark:text-text-tertiary uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                onClick={() => handleSort('desc')}
              >
                <div className="flex items-center gap-1">
                  Description
                  <SortIcon field="desc" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-semibold text-text-tertiary dark:text-text-tertiary uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                onClick={() => handleSort('amount')}
              >
                <div className="flex items-center justify-end gap-1">
                  Amount
                  <SortIcon field="amount" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-light dark:divide-border-dark">
            {paginatedTransactions.map((transaction, index) => {
              const amountData = formatTransactionAmount(transaction.amount);

              return (
                <motion.tr
                  key={index}
                  className="hover:bg-neutral-50 dark:hover:bg-neutral-900/30 transition-colors"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                >
                  <td className="px-4 py-3 text-sm text-text-secondary dark:text-text-tertiary">
                    {formatDate(transaction.date || transaction.transaction_date, 'short')}
                  </td>
                  <td className="px-4 py-3 text-sm text-text-primary dark:text-text-inverse">
                    {transaction.desc || transaction.description}
                  </td>
                  <td className={`px-4 py-3 text-sm text-right font-semibold ${amountData.color}`}>
                    {amountData.formatted}
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-3">
        {paginatedTransactions.map((transaction, index) => {
          const amountData = formatTransactionAmount(transaction.amount);

          return (
            <motion.div
              key={index}
              className="p-4 rounded-xl border border-border-light dark:border-border-dark bg-background-elevated dark:bg-background-dark-secondary"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.02 }}
            >
              <div className="flex justify-between items-start mb-2">
                <p className="text-sm font-medium text-text-primary dark:text-text-inverse">
                  {transaction.desc || transaction.description}
                </p>
                <p className={`text-sm font-bold ${amountData.color}`}>
                  {amountData.formatted}
                </p>
              </div>
              <p className="text-xs text-text-tertiary dark:text-text-tertiary">
                {formatDate(transaction.date || transaction.transaction_date, 'medium')}
              </p>
            </motion.div>
          );
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-text-tertiary dark:text-text-tertiary">
            Showing {startIndex + 1}-{Math.min(endIndex, processedTransactions.length)} of {processedTransactions.length}
          </p>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </Button>

            <span className="text-sm text-text-secondary dark:text-text-tertiary">
              Page {currentPage} of {totalPages}
            </span>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransactionTable;
