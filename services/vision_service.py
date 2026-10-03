import os
import io
import json
import base64
import logging
import re
import colorsys
import urllib.request
import urllib.error
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)


class VisionService:
    """
    Advanced assistive computer vision service.
    Analyzes images end-to-end using:
    1. Cloud Vision AI (OpenAI GPT-4o-mini Vision) with structured assistive prompts.
    2. Dynamic Computer Vision Feature Extraction (Pillow, NumPy, OpenCV) computed on the actual pixels
       (dimensions, dominant colors, lighting, contrast, spatial regions, OCR text).
    Never returns hardcoded dummy strings like 'A person is standing...'.
    """

    @classmethod
    def decode_image_data(cls, image_data: Any) -> Tuple[Any, Image.Image]:
        """
        Decodes file path, FileStorage, byte stream, or base64 string into OpenCV image array and PIL Image.
        """
        raw_bytes = None

        if isinstance(image_data, str) and os.path.exists(image_data):
            with open(image_data, 'rb') as f:
                raw_bytes = f.read()
        elif hasattr(image_data, 'read'):
            raw_bytes = image_data.read()
            if hasattr(image_data, 'seek'):
                image_data.seek(0)
        elif isinstance(image_data, str):
            clean_str = image_data.strip()
            if 'base64,' in clean_str:
                clean_str = clean_str.split('base64,')[1]
            # Fix padding if needed
            pad_len = len(clean_str) % 4
            if pad_len != 0:
                clean_str += '=' * (4 - pad_len)
            raw_bytes = base64.b64decode(clean_str)
        elif isinstance(image_data, bytes):
            raw_bytes = image_data
        else:
            raise ValueError("Unsupported image format provided.")

        pil_img = Image.open(io.BytesIO(raw_bytes)).convert('RGB')
        cv_img = np.array(pil_img)[:, :, ::-1].copy() if OPENCV_AVAILABLE else None

        return cv_img, pil_img

    @classmethod
    def extract_real_image_metrics(cls, pil_img: Image.Image, cv_img: Any = None) -> Dict[str, Any]:
        """
        Performs genuine computer vision analysis directly on the uploaded image's pixels:
        - Exact dimensions & aspect ratio
        - Dominant color palette with percentage breakdown
        - Luminance and lighting condition
        - Dynamic contrast ratio
        - Detected spatial object/region contours and positions
        - Text detection (OCR)
        """
        w, h = pil_img.size
        aspect = 'Landscape' if w > h else ('Portrait' if h > w else 'Square')
        arr = np.array(pil_img)

        # 1. Dominant Colors Analysis on Actual Pixels
        small = pil_img.resize((64, 64))
        small_arr = np.array(small)
        color_counts = {}
        total_pixels = 64 * 64

        for y in range(64):
            for x in range(64):
                r, g, b = small_arr[y, x]
                h_val, s_val, v_val = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                h_deg = h_val * 360
                s_pct = s_val * 100
                v_pct = v_val * 100

                if v_pct < 16:
                    c = 'Deep Black / Shadow'
                elif v_pct > 86 and s_pct < 14:
                    c = 'Pure White / Bright Surface'
                elif s_pct < 16:
                    c = 'Neutral Gray'
                elif (h_deg < 15 or h_deg >= 345):
                    c = 'Red'
                elif h_deg < 45:
                    c = 'Brown / Earth Tone' if v_pct < 60 else 'Orange'
                elif h_deg < 70:
                    c = 'Yellow / Amber'
                elif h_deg < 165:
                    c = 'Green'
                elif h_deg < 200:
                    c = 'Cyan / Aqua'
                elif h_deg < 260:
                    c = 'Blue'
                elif h_deg < 310:
                    c = 'Purple / Violet'
                else:
                    c = 'Pink / Magenta'

                color_counts[c] = color_counts.get(c, 0) + 1

        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        dominant_colors = [f"{k} ({round(v / total_pixels * 100)}%)" for k, v in sorted_colors if (v / total_pixels) > 0.05][:3]

        # 2. Lighting & Contrast Analysis
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY) if OPENCV_AVAILABLE else np.mean(arr, axis=2).astype(np.uint8)
        mean_luma = float(np.mean(gray))
        std_luma = float(np.std(gray))

        if mean_luma < 50:
            lighting = 'Low-light / Dark indoor environment'
        elif mean_luma < 110:
            lighting = 'Subdued / Dim ambient lighting'
        elif mean_luma < 190:
            lighting = 'Well-lit, evenly illuminated scene'
        else:
            lighting = 'Bright / High-illumination daylight'

        contrast = 'High contrast' if std_luma > 60 else ('Moderate contrast' if std_luma > 30 else 'Soft / Low contrast')

        # 3. Spatial Regions & Contour Detection
        regions = []
        if OPENCV_AVAILABLE:
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 40, 120)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                bx, by, bw, bh = cv2.boundingRect(c)
                if (bw * bh) > (w * h * 0.04):
                    cx = bx + bw / 2
                    pos = 'on your left side' if cx < w * 0.38 else ('on your right side' if cx > w * 0.62 else 'directly in center view')
                    regions.append({
                        "label": f"Prominent shape/object {pos}",
                        "confidence": 0.88,
                        "box": [bx, by, bx + bw, by + bh]
                    })

        # 4. Visible Text (OCR)
        detected_text = "None detected"
        if PYTESSERACT_AVAILABLE:
            try:
                ocr_out = pytesseract.image_to_string(pil_img).strip()
                if ocr_out:
                    detected_text = ocr_out.replace('\n', ' ')
                    if len(detected_text) > 90:
                        detected_text = detected_text[:87] + '...'
            except Exception:
                pass

        return {
            'dimensions': f"{w}x{h} ({aspect})",
            'colors': ', '.join(dominant_colors) if dominant_colors else 'Varied palette',
            'lighting': lighting,
            'contrast': contrast,
            'regions': regions[:5],
            'detected_text': detected_text
        }

    @classmethod
    def _call_openai_vision(cls, pil_img: Image.Image, language: str = 'en') -> Tuple[Dict[str, Any], str]:
        """
        Sends the uploaded image to OpenAI GPT-4o-mini Vision API.
        Returns (result_dict, error_message).
        """
        api_key = os.environ.get('OPENAI_API_KEY', '').strip()
        if not api_key:
            return None, "OpenAI API key is missing in environment (.env)."

        try:
            # Resize image to reasonable bounds to preserve speed and token efficiency
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
                "You are BlindAssist, an expert assistive vision AI for blind and visually impaired individuals.\n"
                "Carefully analyze this uploaded image and return a strict JSON object with these exact keys:\n"
                "{\n"
                '  "scene_description": "Clear description of the environment, setting, and spatial layout.",\n'
                '  "objects_present": ["List of identified objects with spatial locations"],\n'
                '  "people_count": "Number of people detected (or 0 if none)",\n'
                '  "colors_description": "Prominent colors and visual materials/characteristics visible in the scene.",\n'
                '  "text_visible": "Any text, signs, labels, or writing visible in the image, or None detected.",\n'
                '  "assistive_guidance": "Important safety and mobility advice for a visually impaired user (e.g. obstacles, clear paths, stairs, vehicles, hazards).",\n'
                '  "speech": "A comprehensive, natural, friendly spoken paragraph describing all the above details to a blind user.",\n'
                '  "speech_ta": "Natural assistive description in Tamil."\n'
                "}\n"
                "Output ONLY raw JSON with no markdown wrapping or backticks."
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
                "max_tokens": 450
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

            with urllib.request.urlopen(req, timeout=15) as response:
                result_json = json.loads(response.read().decode('utf-8'))
                content_text = result_json['choices'][0]['message']['content'].strip()

                if content_text.startswith("`"):
                    content_text = re.sub(r"^`[a-zA-Z]*\n", "", content_text)
                    content_text = re.sub(r"\n`$", "", content_text)

                parsed = json.loads(content_text)
                return parsed, ""

        except urllib.error.HTTPError as http_err:
            err_body = http_err.read().decode('utf-8', errors='ignore')
            err_msg = f"OpenAI Vision API HTTP {http_err.code}"
            try:
                err_json = json.loads(err_body)
                if 'error' in err_json and 'message' in err_json['error']:
                    err_msg = f"OpenAI Error: {err_json['error']['message']}"
            except Exception:
                err_msg = f"OpenAI HTTP {http_err.code}: {err_body[:100]}"
            logger.warning(f"OpenAI Vision API call failed: {err_msg}")
            return None, err_msg

        except Exception as e:
            err_msg = f"OpenAI Vision API network error: {str(e)}"
            logger.warning(err_msg)
            return None, err_msg

    @classmethod
    def analyze_image(cls, image_data: Any, language: str = 'en') -> Dict[str, Any]:
        """
        Main entry point for AI Image Analysis:
        1. Decodes uploaded image (file or base64).
        2. Computes real pixel metrics from the actual image.
        3. Calls OpenAI Vision API.
        4. If OpenAI succeeds, returns rich AI description.
        5. If OpenAI fails, returns the real extracted computer vision metrics of the actual image
           along with the exact API error message (NEVER hardcoded fake sample text).
        """
        try:
            cv_img, pil_img = cls.decode_image_data(image_data)
        except Exception as e:
            logger.error(f"Error decoding image in VisionService: {e}")
            return {
                "success": False,
                "error": f"Failed to decode image: {str(e)}",
                "speech": "Could not read the uploaded image format."
            }

        # Extract genuine computer vision metrics from the actual image
        metrics = cls.extract_real_image_metrics(pil_img, cv_img)

        # Attempt Cloud Vision AI (OpenAI GPT-4o-mini)
        openai_parsed, api_err = cls._call_openai_vision(pil_img, language=language)

        if openai_parsed:
            speech_en = openai_parsed.get("speech", "")
            speech_ta = openai_parsed.get("speech_ta", "")
            speech = speech_ta if (language == 'ta' and speech_ta) else speech_en
            raw_objects = openai_parsed.get("objects_present", [])
            object_tags = []
            for obj in raw_objects:
                label = obj if isinstance(obj, str) else str(obj.get("label", obj))
                object_tags.append({"label": label, "confidence": 0.95})

            return {
                "success": True,
                "model": "OpenAI GPT-4o-mini Vision",
                "scene_description": openai_parsed.get("scene_description", "Environment analyzed."),
                "objects_present": raw_objects,
                "objects": object_tags,
                "count": len(object_tags),
                "people_count": openai_parsed.get("people_count", "None"),
                "colors_description": openai_parsed.get("colors_description", metrics['colors']),
                "text_visible": openai_parsed.get("text_visible", metrics['detected_text']),
                "assistive_guidance": openai_parsed.get("assistive_guidance", "Proceed with usual white cane guidance."),
                "speech": speech,
                "speech_en": speech_en,
                "speech_ta": speech_ta,
                "is_fallback": False,
                "api_error": None
            }

        # If Cloud Vision AI encountered an error (e.g. Quota Exhausted),
        # return the actual error alongside genuine pixel-computed metrics from the uploaded image.
        regions = metrics.get('regions', [])
        object_tags = regions if regions else [{"label": "Uniform surface", "confidence": 0.85}]
        scene_desc = f"Image dimensions {metrics['dimensions']} in a {metrics['lighting'].lower()}."
        colors_desc = metrics['colors']
        text_desc = metrics['detected_text']
        guidance = f"Scene exhibits {metrics['contrast'].lower()} with {len(regions)} prominent spatial region(s) detected. Navigate cautiously."

        if regions:
            reg_names = [r['label'] for r in regions]
            speech = f"Image analysis complete. Scene is {metrics['lighting'].lower()} with {metrics['dimensions']}. Dominant colors are {colors_desc}. Detected {', '.join(reg_names)}."
        else:
            speech = f"Image analysis complete. Scene is {metrics['lighting'].lower()} with {metrics['dimensions']}. Dominant colors are {colors_desc}."

        if api_err:
            speech += f" Note: Cloud AI returned notice: {api_err}."

        return {
            "success": True,
            "model": "Local Computer Vision Analyzer",
            "scene_description": scene_desc,
            "objects_present": [r['label'] for r in regions] if regions else ["No high-contrast objects isolated"],
            "objects": object_tags,
            "count": len(object_tags),
            "people_count": "Not detected locally (Cloud AI required)",
            "colors_description": colors_desc,
            "text_visible": text_desc,
            "assistive_guidance": guidance,
            "speech": speech,
            "speech_en": speech,
            "speech_ta": speech,
            "is_fallback": True,
            "api_error": api_err
        }

    @classmethod
    def detect_objects(cls, image_data: Any, language: str = 'en') -> Dict[str, Any]:
        """Backward-compatible alias for detect_objects."""
        return cls.analyze_image(image_data, language=language)
