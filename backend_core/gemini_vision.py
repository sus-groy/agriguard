"""
Gemini Vision API integration for agricultural pest/disease detection.
This is the MISSING LAYER that connects uploaded images to our diagnostic system.

UPDATED: Uses the NEW google-genai SDK (not google-generativeai)
"""

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Warning: google-genai package not installed.")
    print("   Install with: pip install google-genai")

import os
import json
from typing import List, Dict
from PIL import Image
import io
from dataclasses import dataclass

# Configure Gemini Client
GEMINI_API_KEY = r"AIzaSyBNHd-iUnxSC4mUTLRaK_dAB8nEuyj6QNo"


@dataclass
class GeminiDetectionResult:
    """Structured output from Gemini vision analysis"""
    pest_name: str
    confidence: float
    lesion_percentage: float
    visual_symptoms: List[str]
    lifecycle_stage: str
    urgency_level: str  # "Low", "Medium", "High", "Critical"
    reasoning: str


class GeminiVisionAnalyzer:
    """
    Uses Gemini Vision to analyze agricultural images and detect pests/diseases.
    This is the bridge between farmer's photo and our diagnostic system.
    """
    
    def __init__(self):
        """Initialize Gemini client with agricultural expertise"""
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-genai package is required. "
                "Install with: pip install google-genai"
            )
        
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required.\n"
                "Get your API key from: https://aistudio.google.com/app/apikey\n"
                "Set it with: $env:GEMINI_API_KEY='your-key-here' (PowerShell)\n"
                "Or: set GEMINI_API_KEY=your-key-here (CMD)"
            )
        
        # Initialize the NEW SDK client
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_id = 'models/gemini-2.5-flash'

        
        # System prompt that gives Gemini agricultural expertise
        self.system_instruction = """You are an expert agricultural pathologist and entomologist with 20 years of field experience. 
You specialize in identifying crop pests and diseases from visual symptoms.

When analyzing an image, you MUST provide a structured JSON response with these exact fields:
{
  "pest_name": "Exact name of pest or disease (e.g., 'Fall Armyworm', 'Late Blight', 'Aphids')",
  "confidence": 0.0 to 1.0 (your confidence in this identification),
  "lesion_percentage": 0.0 to 100.0 (percentage of plant tissue showing damage/symptoms),
  "visual_symptoms": ["List", "of", "visible", "symptoms"],
  "lifecycle_stage": "Current stage of pest (e.g., 'Egg', 'Early Larva', 'Late Larva', 'Adult', 'Sporulation')",
  "urgency_level": "Low/Medium/High/Critical based on severity and pest stage",
  "reasoning": "Brief explanation of your diagnosis and urgency assessment"
}

Focus on these common agricultural pests/diseases:
- Fall Armyworm (Spodoptera frugiperda)
- Late Blight (Phytophthora infestans)
- Aphids (various species)
- Whiteflies
- Leaf Miners
- Powdery Mildew
- Bacterial Blight
- Rust diseases

Consider:
1. Visible damage patterns
2. Color changes in leaves/stems
3. Presence of insects or insect parts
4. Fungal growth or spores
5. Overall plant health

Be precise with lesion_percentage - this drives treatment decisions.
Be honest with confidence - if unsure, say so (confidence < 0.7).
"""
    
    def analyze_image(
        self, 
        image_path: str = None, 
        image_bytes: bytes = None,
        crop_type: str = "Unknown"
    ) -> GeminiDetectionResult:
        """
        Analyze agricultural image using Gemini Vision.
        
        Args:
            image_path: Path to image file (OR)
            image_bytes: Raw image bytes
            crop_type: Type of crop being analyzed (helps with context)
        
        Returns:
            GeminiDetectionResult with pest identification
        """
        
        # Load and optimize image
        if image_path:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
        elif not image_bytes:
            raise ValueError("Must provide either image_path or image_bytes")
        
        # Optimize image size
        image_bytes = self._optimize_image_bytes(image_bytes)
        
        # Create prompt with crop context
        user_prompt = f"""Analyze this {crop_type} plant image for pest or disease identification.

Provide your analysis in the exact JSON format specified in the system instructions.

Pay special attention to:
1. Leaf damage patterns (holes, discoloration, wilting)
2. Presence of insects or their signs (frass, egg masses, webbing)
3. Disease symptoms (lesions, spots, mold growth)
4. Overall extent of damage (for lesion_percentage)
5. Stage of pest development (critical for treatment timing)

Be thorough but concise. Farmers need actionable information."""
        
        try:
            # Call Gemini with NEW SDK
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type="image/jpeg"
                            ),
                            types.Part.from_text(text=user_prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.2,
                    top_p=0.8,
                )
            )
            
            # Parse JSON response
            result_text = response.text
            
            # Extract JSON from markdown if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result_json = json.loads(result_text.strip())
            
            # Validate and create result object
            return GeminiDetectionResult(
                pest_name=result_json["pest_name"],
                confidence=float(result_json["confidence"]),
                lesion_percentage=float(result_json["lesion_percentage"]),
                visual_symptoms=result_json["visual_symptoms"],
                lifecycle_stage=result_json.get("lifecycle_stage", "Unknown"),
                urgency_level=result_json.get("urgency_level", "Medium"),
                reasoning=result_json["reasoning"]
            )
        
        except json.JSONDecodeError as e:
            # Fallback: Parse text response if JSON fails
            print(f"⚠️  Warning: Failed to parse JSON from Gemini.")
            print(f"Response: {response.text[:300]}")
            return self._parse_text_response(response.text)
        
        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
            raise
    
    def _optimize_image_bytes(self, image_bytes: bytes) -> bytes:
        """
        Optimize image for Gemini API (reduce size if needed).
        
        Args:
            image_bytes: Raw image bytes
        
        Returns:
            Optimized image bytes
        """
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Gemini works best with images under 4MB
        max_dimension = 2048
        
        if image.width > max_dimension or image.height > max_dimension:
            # Resize while maintaining aspect ratio
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Convert back to bytes
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    
    def _parse_text_response(self, text: str) -> GeminiDetectionResult:
        """
        Fallback parser if Gemini doesn't return JSON.
        Attempts to extract information from natural language.
        """
        return GeminiDetectionResult(
            pest_name="Unknown - Manual Review Required",
            confidence=0.5,
            lesion_percentage=20.0,
            visual_symptoms=["Could not parse symptoms"],
            lifecycle_stage="Unknown",
            urgency_level="Medium",
            reasoning=f"Gemini response could not be parsed. Raw text: {text[:200]}"
        )
    
    def analyze_with_weather_context(
        self,
        image_path: str,
        crop_type: str,
        location: str,
        current_weather: Dict[str, float]
    ) -> GeminiDetectionResult:
        """
        Enhanced analysis that includes weather context for better predictions.
        
        This implements the "Predictive Risk" feature - correlating weather with pest behavior.
        """
        
        # Load image
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Optimize image
        image_bytes = self._optimize_image_bytes(image_bytes)
        
        # Enhanced prompt with weather
        enhanced_prompt = f"""Analyze this {crop_type} plant image considering these environmental conditions:

Location: {location}
Current Temperature: {current_weather.get('temperature', 'Unknown')}°C
Humidity: {current_weather.get('humidity', 'Unknown')}%
Recent Rainfall: {current_weather.get('rainfall_7day', 'Unknown')}mm (last 7 days)

These conditions affect pest behavior:
- High humidity (>80%) favors fungal diseases like Late Blight
- Warm temps (25-30°C) accelerate Fall Armyworm development
- Low humidity (<50%) stresses plants, making them vulnerable to aphids

Factor these conditions into your urgency assessment and lifecycle_stage prediction.

Provide your analysis in the exact JSON format specified in the system instructions.

Pay special attention to:
1. Leaf damage patterns (holes, discoloration, wilting)
2. Presence of insects or their signs (frass, egg masses, webbing)
3. Disease symptoms (lesions, spots, mold growth)
4. Overall extent of damage (for lesion_percentage)
5. Stage of pest development (critical for treatment timing)

Be thorough but concise. Farmers need actionable information."""
        
        try:
            # Call Gemini with weather context
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type="image/jpeg"
                            ),
                            types.Part.from_text(text=enhanced_prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.2,
                    top_p=0.8,
                )
            )
            
            # Parse response
            result_text = response.text
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result_json = json.loads(result_text.strip())
            
            return GeminiDetectionResult(
                pest_name=result_json["pest_name"],
                confidence=float(result_json["confidence"]),
                lesion_percentage=float(result_json["lesion_percentage"]),
                visual_symptoms=result_json["visual_symptoms"],
                lifecycle_stage=result_json.get("lifecycle_stage", "Unknown"),
                urgency_level=result_json.get("urgency_level", "Medium"),
                reasoning=result_json["reasoning"]
            )
        
        except json.JSONDecodeError:
            print(f"⚠️  Warning: Failed to parse JSON.")
            print(f"Response: {response.text[:300]}")
            return self._parse_text_response(response.text)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


def analyze_farmer_image(
    image_path: str,
    crop_type: str,
    location: str,
    growth_stage: str
) -> Dict:
    """
    Main function that processes a farmer's uploaded image.
    This is the entry point that connects Gemini to our diagnostic system.
    
    Usage:
        result = analyze_farmer_image(
            image_path="uploads/tomato_leaf.jpg",
            crop_type="Tomato",
            location="Nagpur",
            growth_stage="Flowering"
        )
    
    Returns:
        Dictionary ready to be converted to DiagnosticInput
    """
    
    # Initialize Gemini analyzer
    analyzer = GeminiVisionAnalyzer()
    
    # Get weather data (using mock for now - replace with real API)
    from logic import mock_get_weather
    weather_data = mock_get_weather(location)
    
    # Analyze image with weather context
    detection = analyzer.analyze_with_weather_context(
        image_path=image_path,
        crop_type=crop_type,
        location=location,
        current_weather=weather_data
    )
    
    print(f"✅ Gemini Detection Complete:")
    print(f"   Pest: {detection.pest_name} (Confidence: {detection.confidence*100:.1f}%)")
    print(f"   Lifecycle Stage: {detection.lifecycle_stage}")
    print(f"   Urgency: {detection.urgency_level}")
    print(f"   Damage: {detection.lesion_percentage:.1f}% affected")
    print(f"   Reasoning: {detection.reasoning}")
    
    # Return data in format compatible with DiagnosticInput
    return {
        "pest_name": detection.pest_name,
        "confidence": detection.confidence,
        "lesion_percentage": detection.lesion_percentage,
        "visual_symptoms": detection.visual_symptoms,
        "crop_type": crop_type,
        "location": location,
        "growth_stage": growth_stage,
        # Additional Gemini-specific insights
        "lifecycle_stage_detected": detection.lifecycle_stage,
        "gemini_urgency": detection.urgency_level,
        "gemini_reasoning": detection.reasoning
    }


# Example usage demonstrating the complete flow
if __name__ == "__main__":
    print("🌾 Gemini Vision Integration Demo")
    print("="*60)
    
    # Check prerequisites
    if not GEMINI_AVAILABLE:
        print("❌ google-genai not installed")
        print("   Run: pip install google-genai pillow")
        exit(1)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set")
        print("   Get key: https://aistudio.google.com/app/apikey")
        print("   Set: $env:GEMINI_API_KEY='your-key' (PowerShell)")
        exit(1)
    
    print("✅ Prerequisites OK")
    print("\n📸 Farmer uploads leaf photo...")
    
    # Try to analyze an image
    try:
        result = analyze_farmer_image(
            image_path=r"C:\Users\goura\OneDrive\Desktop\temp\BuildwithGemini\backend_core\peter_griffin.jpg",
            crop_type="Maize",
            location="Nagpur",
            growth_stage="Vegetative"
        )
        
        print("\n📊 Ready for Diagnostic System:")
        print(json.dumps(result, indent=2))
        
        # Now this result can be passed to generate_diagnostic_report()
        from models import DiagnosticInput, GrowthStage
        from logic import generate_diagnostic_report
        
        diagnostic_input = DiagnosticInput(
            pest_name=result["pest_name"],
            confidence=result["confidence"],
            lesion_percentage=result["lesion_percentage"],
            growth_stage=GrowthStage(result["growth_stage"]),
            crop_type=result["crop_type"],
            crop_value_per_hectare=85000.0,
            location=result["location"],
            visual_symptoms=result["visual_symptoms"]
        )
        
        report = generate_diagnostic_report(diagnostic_input)
        print(f"\n✅ Full diagnostic report generated: {report.diagnostic_id}")
        
    except FileNotFoundError:
        print("\n⚠️  No test image found.")
        print("   Place an image at: test_images/fall_armyworm_damage.jpg")
        print("\n📝 Expected Flow:")
        print("   1. Farmer uploads image → Gemini analyzes")
        print("   2. Gemini returns pest name, confidence, damage %")
        print("   3. Our diagnostic system generates IPM plan")
        print("   4. Farmer receives treatment recommendations")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()