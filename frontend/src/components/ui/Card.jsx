/**
 * Card Component
 *
 * Elevated container with soft shadows and smooth animations.
 * Perfect for grouping content in dashboards, results, and previews.
 *
 * Props:
 * - title: string - Optional card header title
 * - subtitle: string - Optional subtitle text below title
 * - footer: ReactNode - Optional footer content
 * - children: ReactNode - Main card content
 * - variant: 'elevated' | 'bordered' | 'flat' (default: 'elevated')
 * - padding: 'none' | 'sm' | 'md' | 'lg' (default: 'md')
 * - hoverable: boolean - Adds lift effect on hover
 * - className: string - Additional custom classes
 */

import React from 'react';
import { motion } from 'framer-motion';

const Card = ({
  title,
  subtitle,
  footer,
  children,
  variant = 'elevated',
  padding = 'md',
  hoverable = false,
  className = '',
  ...props
}) => {
  /**
   * Base card styles
   */
  const baseStyles = `
    bg-background-elevated dark:bg-background-dark-secondary
    rounded-2xl
    transition-all duration-300
  `;

  /**
   * Variant styles - shadow and border treatments
   */
  const variantStyles = {
    elevated: `
      shadow-md hover:shadow-lg
      dark:shadow-lg dark:hover:shadow-xl
    `,
    bordered: `
      border border-border-light dark:border-border-dark
      hover:border-border-default dark:hover:border-border-light
    `,
    flat: `
      bg-background-muted dark:bg-background-dark
    `,
  };

  /**
   * Padding variants
   */
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  /**
   * Motion variants for mount animation
   * Subtle fade-in with upward slide
   */
  const cardVariants = {
    hidden: {
      opacity: 0,
      y: 20,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        ease: [0.4, 0, 0.2, 1],
      },
    },
  };

  /**
   * Hover animation (only if hoverable prop is true)
   */
  const hoverVariants = hoverable
    ? {
        rest: { y: 0, scale: 1 },
        hover: {
          y: -4,
          scale: 1.01,
          transition: {
            duration: 0.3,
            ease: [0.4, 0, 0.2, 1],
          },
        },
      }
    : {};

  return (
    <motion.div
      className={`
        ${baseStyles}
        ${variantStyles[variant]}
        ${paddingStyles[padding]}
        ${className}
      `}
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={hoverable ? 'hover' : undefined}
      {...(hoverable && { variants: hoverVariants, initial: 'rest' })}
      {...props}
    >
      {/* Card Header */}
      {(title || subtitle) && (
        <div className="mb-4 pb-4 border-b border-border-light dark:border-border-dark">
          {title && (
            <h3 className="text-lg font-semibold text-text-primary dark:text-text-inverse mb-1">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-sm text-text-secondary dark:text-text-tertiary">
              {subtitle}
            </p>
          )}
        </div>
      )}

      {/* Card Body */}
      <div className="text-text-secondary dark:text-text-tertiary">
        {children}
      </div>

      {/* Card Footer */}
      {footer && (
        <div className="mt-4 pt-4 border-t border-border-light dark:border-border-dark">
          {footer}
        </div>
      )}
    </motion.div>
  );
};

export default Card;
