/**
 * HighlightOverlay Component
 *
 * SVG overlay for highlighting extracted fields on PDF pages.
 * Shows bounding boxes with interactive tooltips.
 *
 * Props:
 * - highlights: Array - Highlight data with coordinates
 * - pageWidth: number - PDF page width
 * - pageHeight: number - PDF page height
 * - scale: number - Current zoom scale
 * - onHighlightClick: Function - Click handler
 * - className: string - Additional custom classes
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatConfidence } from '../../utils/formatters';

const HighlightOverlay = ({
  highlights = [],
  pageWidth,
  pageHeight,
  scale = 1,
  onHighlightClick,
  className = '',
}) => {
  const [hoveredHighlight, setHoveredHighlight] = useState(null);

  /**
   * Field type colors
   */
  const fieldColors = {
    card_last4: {
      stroke: 'rgb(59, 130, 246)', // Blue
      fill: 'rgba(59, 130, 246, 0.1)',
    },
    card_variant: {
      stroke: 'rgb(168, 85, 247)', // Purple
      fill: 'rgba(168, 85, 247, 0.1)',
    },
    billing_cycle: {
      stroke: 'rgb(34, 197, 94)', // Green
      fill: 'rgba(34, 197, 94, 0.1)',
    },
    due_date: {
      stroke: 'rgb(239, 68, 68)', // Red
      fill: 'rgba(239, 68, 68, 0.1)',
    },
    transaction: {
      stroke: 'rgb(20, 184, 166)', // Teal
      fill: 'rgba(20, 184, 166, 0.1)',
    },
    default: {
      stroke: 'rgb(148, 163, 184)', // Neutral
      fill: 'rgba(148, 163, 184, 0.1)',
    },
  };

  /**
   * Get color for field type
   */
  const getFieldColor = (fieldType) => {
    return fieldColors[fieldType] || fieldColors.default;
  };

  /**
   * Calculate scaled coordinates
   */
  const getScaledCoords = (coords) => {
    if (!coords || !coords.length) return null;

    const [x0, y0, x1, y1] = coords;

    return {
      x: x0 * scale,
      y: y0 * scale,
      width: (x1 - x0) * scale,
      height: (y1 - y0) * scale,
    };
  };

  if (!pageWidth || !pageHeight) {
    return null;
  }

  return (
    <svg
      className={`absolute top-0 left-0 pointer-events-none ${className}`}
      width={pageWidth * scale}
      height={pageHeight * scale}
      style={{ zIndex: 10 }}
    >
      {highlights.map((highlight, index) => {
        const coords = getScaledCoords(highlight.coords);
        if (!coords) return null;

        const colors = getFieldColor(highlight.fieldType);
        const isHovered = hoveredHighlight === index;

        return (
          <g key={index}>
            {/* Bounding Rectangle */}
            <motion.rect
              x={coords.x}
              y={coords.y}
              width={coords.width}
              height={coords.height}
              fill={colors.fill}
              stroke={colors.stroke}
              strokeWidth={isHovered ? 3 : 2}
              strokeDasharray={isHovered ? '0' : '5,5'}
              rx={4}
              className="pointer-events-auto cursor-pointer transition-all duration-200"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.05 }}
              onMouseEnter={() => setHoveredHighlight(index)}
              onMouseLeave={() => setHoveredHighlight(null)}
              onClick={() => onHighlightClick && onHighlightClick(highlight)}
            />

            {/* Hover Label */}
            <AnimatePresence>
              {isHovered && (
                <motion.g
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 5 }}
                  transition={{ duration: 0.15 }}
                >
                  {/* Label Background */}
                  <rect
                    x={coords.x}
                    y={coords.y - 28}
                    width={Math.max(150, highlight.label?.length * 8 || 100)}
                    height={24}
                    fill="rgb(15, 23, 42)"
                    stroke={colors.stroke}
                    strokeWidth={1}
                    rx={4}
                    className="pointer-events-none"
                  />

                  {/* Field Label */}
                  <text
                    x={coords.x + 8}
                    y={coords.y - 12}
                    fill="white"
                    fontSize={12}
                    fontWeight="600"
                    className="pointer-events-none"
                  >
                    {highlight.label || highlight.fieldType}
                  </text>

                  {/* Confidence Badge */}
                  {highlight.confidence !== undefined && (
                    <text
                      x={coords.x + (highlight.label?.length * 8 || 100) - 40}
                      y={coords.y - 12}
                      fill="rgb(204, 251, 241)"
                      fontSize={11}
                      fontWeight="500"
                      className="pointer-events-none"
                    >
                      {Math.round((typeof highlight.confidence === 'number' && highlight.confidence <= 1
                        ? highlight.confidence * 100
                        : highlight.confidence))}%
                    </text>
                  )}
                </motion.g>
              )}
            </AnimatePresence>
          </g>
        );
      })}
    </svg>
  );
};

export default HighlightOverlay;
