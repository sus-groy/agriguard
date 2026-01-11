"""
Agricultural Diagnostic Engine - Gemini Vision Service

Merged module combining:
- GeminiPromptTemplate functionality
- GeminiIntegration API client

Provides comprehensive Vision-Language Model integration.
"""

import json
import base64
import io
from typing import Optional, Tuple, List
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

from ..core import get_schema_json


# ============================================================================
# PROMPT GENERATION
# ============================================================================

CROP_SPECIFIC_SYMPTOMS = {
    "tomato": {
        "common_diseases": [
            "Early Blight (Alternaria solani)",
            "Late Blight (Phytophthora infestans)",
            "Septoria Leaf Spot",
            "Powdery Mildew",
        ],
        "diagnostic_features": {
            "Early Blight": [
                "Concentric brown rings (target-like lesions)",
                "Yellow halo around lesions",
                "Starts on lower leaves",
            ]
        }
    },
    "potato": {
        "common_diseases": [
            "Late Blight (Phytophthora infestans)",
            "Early Blight (Alternaria)",
            "Powdery Scab",
        ],
        "diagnostic_features": {
            "Late Blight": [
                "Water-soaked spots on leaves",
                "Brown/black lesions",
            ]
        }
    },
    "corn": {
        "common_diseases": [
            "Gray Leaf Spot (Cercospora zeae-maydis)",
            "Northern Corn Leaf Blight",
        ],
        "diagnostic_features": {
            "Gray Leaf Spot": [
                "Rectangular gray lesions",
                "Dark borders",
            ]
        }
    },
    "wheat": {
        "common_diseases": [
            "Powdery Mildew",
            "Fusarium Head Blight (Scab)",
        ],
        "diagnostic_features": {
            "Powdery Mildew": [
                "White powder coating",
            ]
        }
    },
    "lettuce": {
        "common_diseases": [
            "Downy Mildew",
            "Powdery Mildew",
        ],
        "diagnostic_features": {
            "Downy Mildew": [
                "Yellow spots on upper leaf surface",
                "Gray/white fungal growth",
            ]
        }
    }
}


def generate_diagnostic_prompt(crop_type: str) -> str:
    """
    Generate system prompt for Gemini Vision API.
    
    :param crop_type: Crop type (tomato, potato, corn, wheat, lettuce)
    :return: Complete system prompt
    """
    schema = get_schema_json()
    schema_json = json.dumps(schema, indent=2)
    
    crop_lower = crop_type.lower().strip()
    symptoms = CROP_SPECIFIC_SYMPTOMS.get(crop_lower, CROP_SPECIFIC_SYMPTOMS["tomato"])
    
    prompt = f"""You are an expert plant pathologist and agronomist with deep knowledge of crop diseases and pests.

Your task: Analyze this crop image of {crop_type} step-by-step WITHOUT rushing to a diagnosis.

STEP 1: Visual Feature Analysis
- List all visible symptoms: discoloration, lesions, spots, wilting, etc.
- Note their location on the leaf/plant
- Describe size, shape, color patterns
- Look for fungal structures (spores, mycelia)

STEP 2: Quantify Affected Area
- Estimate % of leaf/plant affected by lesions (0-100%)
- Assess disease progression
- Note if symptoms are localized or widespread

STEP 3: Identify Growth Stage
Estimate the crop's current growth stage:
- Seedling: First true leaves visible
- Vegetative: Leafy growth, no flowers
- Flowering: Flowers visible
- Fruiting: Young fruits developing
- Mature: Ready for harvest

STEP 4: Differential Diagnosis
Consider these likely diseases for {crop_type}:
{json.dumps(symptoms['common_diseases'], indent=2)}

For each, assess likelihood based on observed symptoms.

STEP 5: Diagnostic Reasoning
- Which disease best fits the evidence?
- What confidence level (0.0-1.0)?
- Are there conflicting symptoms?
- What additional info would help?

OUTPUT: Provide ONLY valid JSON matching this schema:
{schema_json}

Do NOT include text before or after the JSON block."""
    
    return prompt


def generate_user_message(image_base64: Optional[str] = None) -> dict:
    """
    Generate user message for Gemini API.
    
    :param image_base64: Base64 encoded image string
    :return: Message dict for API
    """
    if image_base64:
        return {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64
                    }
                },
                {
                    "type": "text",
                    "text": "Analyze this crop image using the schema provided. Output valid JSON only."
                }
            ]
        }
    else:
        return {
            "role": "user",
            "content": "Please analyze this crop image according to the provided schema."
        }


def get_gemini_config(crop_type: str) -> dict:
    """
    Get Gemini API configuration.
    
    :param crop_type: Crop type
    :return: Configuration dict
    """
    return {
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.3,
        "max_tokens": 3000,
        "top_p": 0.9,
    }


# ============================================================================
# IMAGE PREPARATION
# ============================================================================

def prepare_image_for_gemini(
    image_path: str,
    max_width: int = 1200,
    max_height: int = 1200,
    quality: int = 85
) -> Tuple[str, str]:
    """
    Prepare image for Gemini Vision API.
    
    :param image_path: Path to image file
    :param max_width: Maximum width
    :param max_height: Maximum height
    :param quality: JPEG quality
    :return: (base64_string, media_type)
    """
    if not Image:
        raise RuntimeError("PIL/Pillow required. Install: pip install Pillow")
    
    image = Image.open(image_path)
    
    if image.width > max_width or image.height > max_height:
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    suffix = Path(image_path).suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    media_type = media_type_map.get(suffix, "image/jpeg")
    
    format_type = "JPEG" if media_type in ("image/jpeg") else suffix[1:].upper()
    
    buffer = io.BytesIO()
    image.save(buffer, format=format_type, quality=quality if format_type == "JPEG" else None)
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    
    return image_base64, media_type


# ============================================================================
# GEMINI CLIENT
# ============================================================================

class GeminiDiagnosticClient:
    """Client for Gemini Vision API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client."""
        self.api_key = api_key
        self.client = None
        
        try:
            if api_key:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel("gemini-2.0-flash-exp")
        except ImportError:
            pass
    
    def analyze_image(
        self,
        image_path: str,
        crop_type: str = "tomato"
    ) -> Tuple[dict, dict]:
        """
        Analyze crop image.
        
        :param image_path: Path to image
        :param crop_type: Crop type
        :return: (diagnostic_result, response_metadata)
        """
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        image_b64, media_type = prepare_image_for_gemini(image_path)
        
        system_prompt = generate_diagnostic_prompt(crop_type)
        user_msg = generate_user_message(image_b64)
        
        response = self.client.generate_content(
            [system_prompt, user_msg],
            generation_config=get_gemini_config(crop_type)
        )
        
        response_text = response.text
        
        # Extract JSON
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        
        if json_start == -1 or json_end <= json_start:
            raise ValueError("No valid JSON in response")
        
        json_str = response_text[json_start:json_end]
        result_dict = json.loads(json_str)
        
        return result_dict, {
            "raw_response": response_text,
            "crop_type": crop_type,
            "image_path": image_path
        }
