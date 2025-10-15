/**
 * FileUploader Component Tests
 *
 * Unit tests for FileUploader component covering:
 * - File selection via input
 * - Drag-and-drop functionality
 * - File validation (type, size)
 * - Upload progress tracking
 * - Error handling
 * - Cancel functionality
 * - Accessibility
 *
 * Test framework: Vitest + React Testing Library
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import FileUploader from '../../src/components/ui/FileUploader';

// Mock useFileUpload hook
vi.mock('../../src/hooks/useFileUpload', () => ({
  default: vi.fn(() => ({
    file: null,
    progress: 0,
    status: 'idle',
    error: null,
    uploadFile: vi.fn(),
    cancelUpload: vi.fn(),
    resetUpload: vi.fn(),
  })),
}));

describe('FileUploader', () => {
  let mockOnFileSelect;

  beforeEach(() => {
    mockOnFileSelect = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render upload zone with instructions', () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      expect(screen.getByText(/Upload your file/i)).toBeInTheDocument();
      expect(screen.getByText(/Drag and drop or click to browse/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Browse Files/i })).toBeInTheDocument();
    });

    it('should display accepted file types and max size', () => {
      render(
        <FileUploader
          onFileSelect={mockOnFileSelect}
          acceptedTypes=".pdf,.csv"
          maxSizeMB={5}
        />
      );

      expect(screen.getByText(/PDF, CSV/i)).toBeInTheDocument();
      expect(screen.getByText(/Max size: 5MB/i)).toBeInTheDocument();
    });

    it('should have accessible file input', () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const fileInput = screen.getByLabelText(/File upload input/i);
      expect(fileInput).toBeInTheDocument();
      expect(fileInput).toHaveAttribute('type', 'file');
    });
  });

  describe('File Selection', () => {
    it('should handle file selection via input', async () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const input = screen.getByLabelText(/File upload input/i);

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockOnFileSelect).toHaveBeenCalledWith(file);
      });
    });

    it('should trigger file input when browse button is clicked', async () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const browseButton = screen.getByRole('button', { name: /Browse Files/i });
      const fileInput = screen.getByLabelText(/File upload input/i);

      const clickSpy = vi.spyOn(fileInput, 'click');

      await userEvent.click(browseButton);

      expect(clickSpy).toHaveBeenCalled();
    });
  });

  describe('Drag and Drop', () => {
    it('should handle drag enter event', () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const dropZone = screen.getByText(/Upload your file/i).closest('div');

      fireEvent.dragEnter(dropZone);

      expect(screen.getByText(/Drop file here/i)).toBeInTheDocument();
    });

    it('should handle file drop', async () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const dropZone = screen.getByText(/Upload your file/i).closest('div');

      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: [file],
        },
      });

      await waitFor(() => {
        expect(mockOnFileSelect).toHaveBeenCalledWith(file);
      });
    });

    it('should reset drag state after drop', () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const dropZone = screen.getByText(/Upload your file/i).closest('div');

      fireEvent.dragEnter(dropZone);
      expect(screen.getByText(/Drop file here/i)).toBeInTheDocument();

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: [file],
        },
      });

      expect(screen.queryByText(/Drop file here/i)).not.toBeInTheDocument();
    });
  });

  describe('File Validation', () => {
    it('should reject file with invalid type', async () => {
      render(
        <FileUploader
          onFileSelect={mockOnFileSelect}
          acceptedTypes=".pdf"
        />
      );

      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const input = screen.getByLabelText(/File upload input/i);

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText(/File type not supported/i)).toBeInTheDocument();
      });

      expect(mockOnFileSelect).not.toHaveBeenCalled();
    });

    it('should reject file exceeding size limit', async () => {
      render(
        <FileUploader
          onFileSelect={mockOnFileSelect}
          maxSizeMB={1}
        />
      );

      // Create a file larger than 1MB
      const largeContent = new Array(2 * 1024 * 1024).fill('a').join('');
      const file = new File([largeContent], 'large.pdf', { type: 'application/pdf' });
      const input = screen.getByLabelText(/File upload input/i);

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText(/File size must be less than 1MB/i)).toBeInTheDocument();
      });

      expect(mockOnFileSelect).not.toHaveBeenCalled();
    });

    it('should accept valid file', async () => {
      render(
        <FileUploader
          onFileSelect={mockOnFileSelect}
          acceptedTypes=".pdf"
          maxSizeMB={10}
        />
      );

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const input = screen.getByLabelText(/File upload input/i);

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockOnFileSelect).toHaveBeenCalledWith(file);
      });

      expect(screen.queryByText(/File type not supported/i)).not.toBeInTheDocument();
    });
  });

  describe('Upload Progress', () => {
    it('should display file information during upload', async () => {
      const mockUseFileUpload = await import('../../src/hooks/useFileUpload');
      mockUseFileUpload.default.mockReturnValue({
        file: new File(['test'], 'test.pdf', { type: 'application/pdf' }),
        progress: 50,
        status: 'uploading',
        error: null,
        uploadFile: vi.fn(),
        cancelUpload: vi.fn(),
        resetUpload: vi.fn(),
      });

      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      expect(screen.getByText('test.pdf')).toBeInTheDocument();
      expect(screen.getByText(/50%/)).toBeInTheDocument();
    });

    it('should show cancel button during upload', async () => {
      const mockCancelUpload = vi.fn();
      const mockUseFileUpload = await import('../../src/hooks/useFileUpload');
      mockUseFileUpload.default.mockReturnValue({
        file: new File(['test'], 'test.pdf', { type: 'application/pdf' }),
        progress: 50,
        status: 'uploading',
        error: null,
        uploadFile: vi.fn(),
        cancelUpload: mockCancelUpload,
        resetUpload: vi.fn(),
      });

      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      expect(cancelButton).toBeInTheDocument();

      await userEvent.click(cancelButton);
      expect(mockCancelUpload).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should display upload error', async () => {
      const mockUseFileUpload = await import('../../src/hooks/useFileUpload');
      mockUseFileUpload.default.mockReturnValue({
        file: new File(['test'], 'test.pdf', { type: 'application/pdf' }),
        progress: 0,
        status: 'error',
        error: 'Network error',
        uploadFile: vi.fn(),
        cancelUpload: vi.fn(),
        resetUpload: vi.fn(),
      });

      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    });

    it('should show remove button after error', async () => {
      const mockResetUpload = vi.fn();
      const mockUseFileUpload = await import('../../src/hooks/useFileUpload');
      mockUseFileUpload.default.mockReturnValue({
        file: new File(['test'], 'test.pdf', { type: 'application/pdf' }),
        progress: 0,
        status: 'error',
        error: 'Upload failed',
        uploadFile: vi.fn(),
        cancelUpload: vi.fn(),
        resetUpload: mockResetUpload,
      });

      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const removeButton = screen.getByRole('button', { name: /Remove/i });
      await userEvent.click(removeButton);

      expect(mockResetUpload).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const input = screen.getByLabelText(/File upload input/i);
      expect(input).toBeInTheDocument();
    });

    it('should be keyboard navigable', async () => {
      render(<FileUploader onFileSelect={mockOnFileSelect} />);

      const browseButton = screen.getByRole('button', { name: /Browse Files/i });

      // Tab to button
      await userEvent.tab();
      expect(browseButton).toHaveFocus();

      // Enter to trigger
      await userEvent.keyboard('{Enter}');
      // File input should be triggered (tested via click spy earlier)
    });
  });
});
