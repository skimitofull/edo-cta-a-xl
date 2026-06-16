from __future__ import annotations

import io
from typing import List, Dict, Any

import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image


def _preprocess_image(pil_image: Image.Image) -> Image.Image:
    img = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 3)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    return Image.fromarray(thresh)


def pdf_to_ocr_pages(pdf_bytes: bytes, dpi: int = 250, lang: str = "spa") -> List[Dict[str, Any]]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: List[Dict[str, Any]] = []

    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    for idx, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        clean_image = _preprocess_image(image)

        config = "--oem 3 --psm 6"
        text = pytesseract.image_to_string(clean_image, lang=lang, config=config)

        pages.append({
            "page": idx,
            "text": text,
        })

    return pages
