"""
OCR utilities – extract text from uploaded images and PDFs using EasyOCR.
For digital PDFs, pdfplumber is tried first (faster, no OCR needed).
"""
from __future__ import annotations
import io
import numpy as np
from pathlib import Path


# EasyOCR reader is loaded lazily because it's slow to initialise
_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _reader


def image_bytes_to_array(image_bytes: bytes) -> np.ndarray:
    """Convert raw image bytes to an RGB numpy array."""
    from PIL import Image
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(img)


def pdf_to_images(pdf_bytes: bytes) -> list[np.ndarray]:
    """
    Rasterize each page of a PDF to an RGB numpy array.
    Requires pdf2image and poppler. Returns an empty list on failure.
    """
    try:
        from pdf2image import convert_from_bytes
        pages = convert_from_bytes(pdf_bytes, dpi=200)
        return [np.array(p.convert("RGB")) for p in pages]
    except Exception:
        return []


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Main entry point: given raw file bytes and the original filename,
    return the full extracted text as a string.

    For PDFs: tries pdfplumber first (fast text extraction), then falls
    back to EasyOCR on rasterized pages for scanned documents.
    For images: runs EasyOCR directly.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        # Try pdfplumber first – works great for digital PDFs
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages_text = [p.extract_text() or "" for p in pdf.pages]
                combined = "\n".join(pages_text).strip()
                if combined:
                    return combined
        except Exception:
            pass

        # Fall back to OCR on rasterized pages (for scanned PDFs)
        images = pdf_to_images(file_bytes)
        if not images:
            return "[Could not extract text from PDF – please ensure poppler is installed]"

        reader = _get_reader()
        all_text: list[str] = []
        for img in images:
            results = reader.readtext(img, detail=0, paragraph=True)
            all_text.append("\n".join(results))
        return "\n\n--- Page Break ---\n\n".join(all_text)

    else:
        # Image file – run EasyOCR directly
        img_array = image_bytes_to_array(file_bytes)
        reader = _get_reader()
        results = reader.readtext(img_array, detail=0, paragraph=True)
        return "\n".join(results)
