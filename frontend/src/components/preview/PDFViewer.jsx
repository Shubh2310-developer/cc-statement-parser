/**
 * PDFViewer Component
 *
 * PDF document viewer with navigation, zoom, and highlight overlay.
 * Uses react-pdf or PDF.js for rendering.
 *
 * Props:
 * - fileUrl: string - PDF file URL or path
 * - highlights: Array - Highlight data for overlay
 * - onHighlightClick: Function - Highlight click handler
 * - className: string - Additional custom classes
 *
 * Note: This component requires 'react-pdf' or 'pdfjs-dist' package.
 * Install with: npm install react-pdf pdfjs-dist
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Button from '../ui/Button';
import Spinner from '../ui/Spinner';
import HighlightOverlay from './HighlightOverlay';

/**
 * Placeholder PDF Viewer Implementation
 *
 * In production, integrate with:
 * - react-pdf: https://github.com/wojtekmaj/react-pdf
 * - OR pdfjs-dist: https://mozilla.github.io/pdf.js/
 *
 * Example with react-pdf:
 * import { Document, Page, pdfjs } from 'react-pdf';
 * pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;
 */

const PDFViewer = ({
  fileUrl,
  highlights = [],
  onHighlightClick,
  className = '',
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [numPages, setNumPages] = useState(null);
  const [scale, setScale] = useState(1.0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Page dimensions (will be updated when PDF loads)
  const [pageWidth, setPageWidth] = useState(600);
  const [pageHeight, setPageHeight] = useState(800);

  /**
   * Handle PDF load success
   */
  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setLoading(false);
  };

  /**
   * Handle PDF load error
   */
  const onDocumentLoadError = (error) => {
    setError('Failed to load PDF document');
    setLoading(false);
    console.error('PDF load error:', error);
  };

  /**
   * Navigation handlers
   */
  const goToPreviousPage = () => {
    setCurrentPage((prev) => Math.max(1, prev - 1));
  };

  const goToNextPage = () => {
    setCurrentPage((prev) => Math.min(numPages || prev, prev + 1));
  };

  /**
   * Zoom handlers
   */
  const handleZoomIn = () => {
    setScale((prev) => Math.min(3, prev + 0.25));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(0.5, prev - 0.25));
  };

  const handleResetZoom = () => {
    setScale(1.0);
  };

  /**
   * Filter highlights for current page
   */
  const currentPageHighlights = highlights.filter(
    (h) => h.page === currentPage || h.pageNumber === currentPage || !h.page
  );

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-border-light dark:border-border-dark bg-background-muted dark:bg-background-dark">
        {/* Page Navigation */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={goToPreviousPage}
            disabled={currentPage === 1 || loading}
            leftIcon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            }
          >
            Previous
          </Button>

          <div className="flex items-center gap-2 px-3 py-1 bg-background-elevated dark:bg-background-dark-secondary rounded-lg border border-border-light dark:border-border-dark">
            <span className="text-sm font-medium text-text-primary dark:text-text-inverse">
              Page {currentPage}
            </span>
            {numPages && (
              <span className="text-sm text-text-tertiary dark:text-text-tertiary">
                of {numPages}
              </span>
            )}
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={goToNextPage}
            disabled={currentPage === numPages || loading}
            rightIcon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            }
          >
            Next
          </Button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomOut}
            disabled={scale <= 0.5 || loading}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
            </svg>
          </Button>

          <span className="text-sm font-medium text-text-secondary dark:text-text-tertiary min-w-16 text-center">
            {Math.round(scale * 100)}%
          </span>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomIn}
            disabled={scale >= 3 || loading}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
            </svg>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleResetZoom}
            disabled={scale === 1 || loading}
          >
            Reset
          </Button>
        </div>
      </div>

      {/* PDF Canvas Area */}
      <div className="flex-1 overflow-auto bg-neutral-100 dark:bg-neutral-900 p-8">
        <div className="flex justify-center">
          <div className="relative inline-block shadow-2xl">
            {/* Loading State */}
            {loading && (
              <div className="flex flex-col items-center justify-center h-96 w-full bg-background-elevated dark:bg-background-dark rounded-lg">
                <Spinner size="lg" />
                <p className="mt-4 text-sm text-text-tertiary dark:text-text-tertiary">
                  Loading PDF...
                </p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <motion.div
                className="flex flex-col items-center justify-center h-96 w-full bg-error-light dark:bg-error-dark/20 rounded-lg p-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <svg className="w-16 h-16 text-error-DEFAULT mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <p className="text-error-dark dark:text-error-DEFAULT font-medium">
                  {error}
                </p>
              </motion.div>
            )}

            {/* PDF Placeholder / Integration Point */}
            {!loading && !error && (
              <div className="relative">
                {/*
                  INTEGRATION POINT: Replace with actual PDF rendering

                  Example with react-pdf:
                  <Document
                    file={fileUrl}
                    onLoadSuccess={onDocumentLoadSuccess}
                    onLoadError={onDocumentLoadError}
                  >
                    <Page
                      pageNumber={currentPage}
                      scale={scale}
                      onLoadSuccess={({ width, height }) => {
                        setPageWidth(width);
                        setPageHeight(height);
                      }}
                    />
                  </Document>
                */}

                {/* Placeholder Canvas */}
                <div
                  className="bg-white dark:bg-neutral-800 shadow-lg"
                  style={{
                    width: pageWidth * scale,
                    height: pageHeight * scale,
                  }}
                >
                  <div className="flex flex-col items-center justify-center h-full text-center p-8">
                    <svg className="w-24 h-24 text-neutral-300 dark:text-neutral-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <h3 className="text-lg font-semibold text-text-primary dark:text-text-inverse mb-2">
                      PDF Viewer
                    </h3>
                    <p className="text-sm text-text-tertiary dark:text-text-tertiary max-w-md">
                      Integrate react-pdf or PDF.js library to display PDF content here.
                      File: {fileUrl || 'No file loaded'}
                    </p>
                  </div>
                </div>

                {/* Highlight Overlay */}
                {currentPageHighlights.length > 0 && (
                  <HighlightOverlay
                    highlights={currentPageHighlights}
                    pageWidth={pageWidth}
                    pageHeight={pageHeight}
                    scale={scale}
                    onHighlightClick={onHighlightClick}
                  />
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="px-4 py-2 border-t border-border-light dark:border-border-dark bg-background-muted dark:bg-background-dark">
        <div className="flex items-center justify-between text-xs text-text-tertiary dark:text-text-tertiary">
          <span>
            {fileUrl ? `File: ${fileUrl.split('/').pop()}` : 'No file loaded'}
          </span>
          {currentPageHighlights.length > 0 && (
            <span>
              {currentPageHighlights.length} highlight{currentPageHighlights.length !== 1 ? 's' : ''} on this page
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;
