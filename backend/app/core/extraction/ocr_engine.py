"""OCR engine module using pytesseract for scanned PDFs.

This module handles OCR (Optical Character Recognition) for scanned PDF documents.
It converts PDF pages to images, preprocesses them for better OCR accuracy,
and extracts text using Tesseract OCR.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
from io import BytesIO

# Import PyMuPDF - avoid conflict with frontend directory
try:
    import pymupdf as fitz
except ImportError:
    import fitz
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class OCRResult:
    """Result from OCR processing."""

    text: str
    confidence: float
    page_num: int
    processing_time: float = 0.0


@dataclass
class OCRPageResult:
    """OCR result for a single page."""

    page_num: int
    text: str
    confidence: float
    bbox_data: Optional[dict] = None  # Detailed OCR data with bounding boxes


class OCREngine:
    """OCR engine for extracting text from scanned PDF documents."""

    def __init__(self):
        """Initialize OCR engine."""
        self.settings = get_settings()
        self.dpi = self.settings.OCR_DPI
        self.language = self.settings.OCR_LANGUAGE

        # Verify tesseract is installed
        try:
            pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {pytesseract.get_tesseract_version()}")
        except Exception as e:
            logger.warning(f"Tesseract may not be properly installed: {e}")

    def extract_text_from_pdf(
        self,
        pdf_bytes: bytes,
        preprocess: bool = True
    ) -> List[OCRPageResult]:
        """Extract text from scanned PDF using OCR.

        Args:
            pdf_bytes: PDF file content as bytes
            preprocess: Whether to preprocess images for better OCR

        Returns:
            List of OCRPageResult objects for each page

        Raises:
            RuntimeError: If OCR processing fails
        """
        if not self.settings.OCR_ENABLED:
            logger.warning("OCR is disabled in settings")
            return []

        logger.info(f"Starting OCR extraction from PDF bytes")

        try:
            # Convert PDF pages to images
            images = self._pdf_to_images(pdf_bytes)

            results = []
            for page_num, image in enumerate(images, start=1):
                logger.info(f"Processing page {page_num}/{len(images)} with OCR")

                # Preprocess image if requested
                if preprocess:
                    processed_image = self._preprocess_image(image)
                else:
                    processed_image = image

                # Run OCR
                ocr_result = self._run_ocr(processed_image, page_num)
                results.append(ocr_result)

            logger.info(f"OCR extraction completed: {len(results)} pages processed")
            return results

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise RuntimeError(f"OCR processing failed: {e}")

    def extract_text_from_image(
        self,
        image_path: Path,
        preprocess: bool = True
    ) -> OCRPageResult:
        """Extract text from a single image file.

        Args:
            image_path: Path to image file
            preprocess: Whether to preprocess image

        Returns:
            OCRPageResult object

        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        logger.info(f"Running OCR on image: {image_path}")

        try:
            image = Image.open(image_path)

            if preprocess:
                image = self._preprocess_image(image)

            result = self._run_ocr(image, page_num=1)
            return result

        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            raise RuntimeError(f"Image OCR failed: {e}")

    def _pdf_to_images(self, pdf_bytes: bytes) -> List[Image.Image]:
        """Convert PDF pages to PIL Images.

        Args:
            pdf_bytes: PDF file content as bytes

        Returns:
            List of PIL Image objects
        """
        images = []

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Render page to image at specified DPI
                # Calculate zoom factor from DPI (72 is default)
                zoom = self.dpi / 72
                mat = fitz.Matrix(zoom, zoom)

                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(BytesIO(img_data))

                images.append(image)
                logger.debug(f"Converted page {page_num + 1} to image: {image.size}")

            doc.close()

        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            raise

        return images

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy.

        Applies:
        - Grayscale conversion
        - Noise reduction
        - Binarization (adaptive thresholding)
        - Deskewing

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert PIL to OpenCV format
            img_array = np.array(image)

            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Noise removal - Gaussian blur
            denoised = cv2.GaussianBlur(gray, (5, 5), 0)

            # Adaptive thresholding for binarization
            # This works better than simple thresholding for varying lighting
            binary = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            # Deskew the image
            deskewed = self._deskew_image(binary)

            # Convert back to PIL Image
            result = Image.fromarray(deskewed)

            logger.debug(f"Image preprocessed: {result.size}")
            return result

        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image

    def _deskew_image(self, img_array: np.ndarray) -> np.ndarray:
        """Deskew an image by detecting and correcting rotation.

        Args:
            img_array: Grayscale image array

        Returns:
            Deskewed image array
        """
        try:
            # Invert image (text should be white on black for this)
            inverted = cv2.bitwise_not(img_array)

            # Find all non-zero points (text pixels)
            coords = np.column_stack(np.where(inverted > 0))

            if len(coords) == 0:
                return img_array

            # Find minimum area rectangle around text
            angle = cv2.minAreaRect(coords)[-1]

            # Correct angle
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            # Only deskew if angle is significant (> 0.5 degrees)
            if abs(angle) < 0.5:
                return img_array

            # Rotate image to deskew
            (h, w) = img_array.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                img_array,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )

            logger.debug(f"Image deskewed by {angle:.2f} degrees")
            return rotated

        except Exception as e:
            logger.warning(f"Deskewing failed: {e}")
            return img_array

    def _run_ocr(self, image: Image.Image, page_num: int) -> OCRPageResult:
        """Run Tesseract OCR on an image.

        Args:
            image: PIL Image object
            page_num: Page number

        Returns:
            OCRPageResult object
        """
        import time
        start_time = time.time()

        try:
            # Configure Tesseract
            custom_config = r'--oem 3 --psm 6'  # OEM 3 = Default, PSM 6 = Assume uniform block of text

            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=custom_config
            )

            # Get detailed data with confidence scores
            try:
                data = pytesseract.image_to_data(
                    image,
                    lang=self.language,
                    config=custom_config,
                    output_type=pytesseract.Output.DICT
                )

                # Calculate average confidence
                confidences = [
                    int(conf) for conf in data['conf']
                    if conf != '-1' and str(conf).isdigit()
                ]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                avg_confidence = avg_confidence / 100.0  # Normalize to 0-1

            except Exception as e:
                logger.warning(f"Could not get OCR confidence data: {e}")
                data = None
                avg_confidence = 0.5  # Default confidence

            processing_time = time.time() - start_time

            result = OCRPageResult(
                page_num=page_num,
                text=text.strip(),
                confidence=avg_confidence,
                bbox_data=data
            )

            logger.info(
                f"OCR completed for page {page_num}: "
                f"{len(text)} chars, confidence: {avg_confidence:.2f}, "
                f"time: {processing_time:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"OCR failed for page {page_num}: {e}")
            # Return empty result instead of failing
            return OCRPageResult(
                page_num=page_num,
                text="",
                confidence=0.0,
                bbox_data=None
            )

    def enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """Enhance image quality for better OCR.

        Args:
            image: PIL Image object

        Returns:
            Enhanced PIL Image
        """
        try:
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)

            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)

            # Apply unsharp mask for better text clarity
            image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

            return image

        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return image

    def get_text_with_boxes(
        self,
        image: Image.Image,
        min_confidence: float = 0.5
    ) -> List[dict]:
        """Extract text with bounding boxes.

        Args:
            image: PIL Image object
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of dicts with text and bounding box info
        """
        try:
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )

            results = []
            n_boxes = len(data['text'])

            for i in range(n_boxes):
                text = data['text'][i].strip()
                conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0

                if text and (conf / 100.0) >= min_confidence:
                    results.append({
                        'text': text,
                        'confidence': conf / 100.0,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'block_num': data['block_num'][i],
                        'line_num': data['line_num'][i],
                        'word_num': data['word_num'][i]
                    })

            return results

        except Exception as e:
            logger.error(f"Failed to extract text with boxes: {e}")
            return []
