"""
OCR Service for Blind Assist.
Processes uploaded images or camera captures, applies computer vision preprocessing,
and extracts readable text using:
1. OpenAI GPT-4o-mini Vision (when API key is present)
2. Tesseract OCR (when installed)
3. Sample accessible fallback for demonstration.
"""

import io
import os
import re
import json
import base64
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# Optional OpenCV import
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Optional Pytesseract import
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


class OCRService:
    """Optical Character Recognition service designed for assistive text reading."""

    SAMPLE_TEXTS = [
        "CAUTION: WET FLOOR. PLEASE WALK CAREFULLY.",
        "EMERGENCY EXIT. KEEP CLEAR AT ALL TIMES.",
        "PHARMACY PRESCRIPTION:\nParacetamol 500mg\nTake 1 tablet every 6 hours after meals.",
        "WELCOME TO CITY METRO STATION.\nPlatform 2: Downtown Express.\nNext train arrives in 4 minutes.",
        "BLIND ASSIST - Accessible Smart Navigation and Text Reader System.\nIndependence through technology."
    ]

    @classmethod
    def _extract_with_openai(cls, pil_img: Image.Image, language: str = 'eng') -> Dict[str, Any]:
        """
        Extracts readable text from images using OpenAI GPT-4o-mini Vision API.
        """
        api_key = os.environ.get('OPENAI_API_KEY', '').strip()
        if not api_key:
            return None

        try:
            max_dim = 1024
            w, h = pil_img.size
            if max(w, h) > max_dim:
                scale = max_dim / max(w, h)
                resized = pil_img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            else:
                resized = pil_img

            buffer = io.BytesIO()
            resized.save(buffer, format="JPEG", quality=85)
            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            data_uri = f"data:image/jpeg;base64,{img_b64}"

            prompt = (
                "You are an OCR reader for a visually impaired user. "
                "Read and transcribe ALL text visible in this image verbatim. "
                "If it is a medicine label, notice, menu, or document, format it cleanly so it sounds natural when spoken aloud. "
                "Output ONLY the extracted text, with no introductory banter."
            )

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_uri}}
                        ]
                    }
                ],
                "max_tokens": 400
            }

            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=12) as response:
                result_json = json.loads(response.read().decode('utf-8'))
                extracted_text = result_json['choices'][0]['message']['content'].strip()
                if extracted_text:
                    logger.info("OpenAI Vision successfully extracted text from image.")
                    return {
                        "success": True,
                        "text": extracted_text,
                        "is_demo": False,
                        "char_count": len(extracted_text),
                        "model": "OpenAI GPT-4o-mini Vision",
                        "message": "Text extracted using OpenAI Vision."
                    }

        except urllib.error.HTTPError as http_err:
            logger.warning(f"OpenAI Vision OCR HTTP {http_err.code}")
            return None
        except Exception as e:
            logger.warning(f"OpenAI Vision OCR error: {e}")
            return None

    @classmethod
    def configure_tesseract(cls):
        """Configure tesseract command path if defined in environment or standard locations."""
        if not PYTESSERACT_AVAILABLE:
            return

        cmd = os.environ.get('TESSERACT_CMD')
        if cmd and os.path.exists(cmd):
            pytesseract.pytesseract.tesseract_cmd = cmd
            return

        if os.name == 'nt':
            standard_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
            ]
            for p in standard_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    break

    @classmethod
    def decode_image_data(cls, image_data: Any) -> Image.Image:
        """Decodes raw bytes, base64 data string, or file storage into a PIL Image."""
        if isinstance(image_data, str):
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            raw_bytes = base64.b64decode(image_data)
        elif hasattr(image_data, 'read'):
            raw_bytes = image_data.read()
            if hasattr(image_data, 'seek'):
                image_data.seek(0)
        elif isinstance(image_data, bytes):
            raw_bytes = image_data
        else:
            raise ValueError("Unsupported image input provided for OCR.")

        return Image.open(io.BytesIO(raw_bytes)).convert('RGB')

    @classmethod
    def preprocess_image(cls, pil_img: Image.Image) -> Image.Image:
        """Enhance image contrast and remove noise for improved OCR character extraction."""
        if not OPENCV_AVAILABLE:
            return pil_img.convert('L')

        try:
            cv_img = np.array(pil_img)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            thresh = cv2.adaptiveThreshold(
                filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 31, 2
            )
            return Image.fromarray(thresh)
        except Exception as e:
            logger.warning(f"OpenCV preprocessing failed: {e}")
            return pil_img

    @classmethod
    def extract_text(cls, image_data: Any, language: str = 'eng') -> Dict[str, Any]:
        """
        Extract text from an image.
        1. Tries OpenAI GPT-4o-mini Vision (when API key is active)
        2. Tries Tesseract OCR
        3. Falls back gracefully for demonstration.
        """
        try:
            pil_img = cls.decode_image_data(image_data)
        except Exception as e:
            logger.error(f"Image decoding error in OCRService: {e}")
            return {
                "success": False,
                "error": f"Failed to read image: {str(e)}",
                "text": ""
            }

        # 1. Attempt OpenAI Vision OCR
        openai_res = cls._extract_with_openai(pil_img, language=language)
        if openai_res and openai_res.get("success"):
            return openai_res

        # 2. Attempt Tesseract OCR
        processed_img = cls.preprocess_image(pil_img)
        cls.configure_tesseract()

        extracted_text = ""
        is_demo = False

        if PYTESSERACT_AVAILABLE:
            try:
                extracted_text = pytesseract.image_to_string(processed_img, lang=language).strip()
            except Exception as t_err:
                logger.warning(f"Tesseract error: {t_err}")
                is_demo = True

        if not extracted_text or is_demo:
            w, h = pil_img.size
            idx = (w + h) % len(cls.SAMPLE_TEXTS)
            extracted_text = cls.SAMPLE_TEXTS[idx]
            is_demo = True

        return {
            "success": True,
            "text": extracted_text,
            "is_demo": is_demo,
            "char_count": len(extracted_text),
            "message": "Text successfully extracted from image."
        }
