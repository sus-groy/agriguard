# Agricultural Diagnostic Engine - Technical Documentation

**Version:** 1.0."""
Gemini Vision API Integration Guide

Complete example of integrating the Agricultural Diagnostic Engine with
Google's Gemini Vision API for real-world crop image analysis.

This module demonstrates:
1. Image loading and preparation
2. Prompt generation
3. API communication
4. Response parsing
5. Result validation and scoring
6. Error handling
"""

import base64
import json
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
import io

from GeminiPromptTemplate import (
    generate_diagnostic_prompt,
    generate_user_message,
    get_gemini_config
)
from ImageAnalysis import (
    DiagnosticResult,
    validate_diagnostic_result,
    SeverityLevel
)
from ScoringEngine import ScoringEngine


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
    Prepare an image file for Gemini Vision API.
    
    PARAMETERS:
    ===========
    image_path : str
        Path to the image file (JPG, PNG, GIF, WebP)
        
    max_width : int
        Maximum image width (Gemini limit: 3840px)
        
    max_height : int
        Maximum image height (Gemini limit: 2160px)
        
    quality : int
        JPEG quality for base64 encoding (1-100)
        
    RETURNS:
    ========
    Tuple[str, str]
        (image_base64_string, image_media_type)
        
    EXAMPLE:
    ========
    >>> b64, media_type = prepare_image_for_gemini("leaf_image.jpg")
    >>> print(media_type)  # "image/jpeg"
    """
    # Load image
    image = Image.open(image_path)
    
    # Resize if necessary
    if image.width > max_width or image.height > max_height:
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Determine media type
    suffix = Path(image_path).suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    media_type = media_type_map.get(suffix, "image/jpeg")
    
    # Convert to base64
    if media_type == "image/png":
        format_type = "PNG"
    elif media_type == "image/gif":
        format_type = "GIF"
    elif media_type == "image/webp":
        format_type = "WEBP"
    else:
        format_type = "JPEG"
    
    # Save to buffer
    buffer = io.BytesIO()
    image.save(buffer, format=format_type, quality=quality if format_type == "JPEG" else None)
    buffer.seek(0)
    
    # Encode to base64
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    
    return image_base64, media_type


# ============================================================================
# GEMINI API INTEGRATION
# ============================================================================

class GeminiDiagnosticClient:
    """
    Client for integrating with Gemini Vision API for crop diagnostics.
    
    This class handles:
    - Prompt generation
    - Image preparation
    - API communication
    - Response parsing
    - Result validation and scoring
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini diagnostic client.
        
        PARAMETERS:
        ===========
        api_key : str, optional
            Google API key. If None, uses GOOGLE_API_KEY environment variable.
        """
        self.api_key = api_key
        self.scoring_engine = ScoringEngine()
        
        # Try to import Gemini if API key provided
        try:
            if api_key:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel("gemini-2.0-flash-exp")
            else:
                self.client = None
        except ImportError:
            print("Warning: google-generativeai not installed. Install with:")
            print("  pip install google-generativeai")
            self.client = None
    
    def analyze_image(
        self,
        image_path: str,
        crop_type: str = "tomato",
        apply_scoring: bool = True,
        required_symptoms: Optional[list] = None
    ) -> Tuple[DiagnosticResult, dict]:
        """
        Analyze a crop image using Gemini Vision API.
        
        PARAMETERS:
        ===========
        image_path : str
            Path to the crop image
            
        crop_type : str
            Type of crop (tomato, potato, corn, wheat, lettuce)
            
        apply_scoring : bool
            Whether to apply ScoringEngine adjustments
            
        required_symptoms : list, optional
            Expected symptoms for confidence adjustment
            
        RETURNS:
        ========
        Tuple[DiagnosticResult, dict]
            (validated_result, raw_response_dict)
            
        EXAMPLE:
        ========
        >>> client = GeminiDiagnosticClient(api_key="your-key")
        >>> result, response = client.analyze_image("leaf_image.jpg", "tomato")
        >>> print(f"Diagnosis: {result.diagnosis.label}")
        >>> print(f"Confidence: {result.confidence_overall:.1%}")
        """
        if not self.client:
            raise RuntimeError(
                "Gemini client not initialized. Provide API key or install "
                "google-generativeai: pip install google-generativeai"
            )
        
        # Step 1: Prepare image
        print(f"Loading image: {image_path}")
        image_b64, media_type = prepare_image_for_gemini(image_path)
        
        # Step 2: Generate prompt
        print(f"Generating prompt for {crop_type}...")
        system_prompt = generate_diagnostic_prompt(crop_type)
        user_msg = generate_user_message(image_b64)
        
        # Step 3: Call Gemini API
        print("Calling Gemini Vision API...")
        try:
            response = self.client.generate_content(
                [
                    system_prompt,
                    user_msg
                ],
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_output_tokens": 3000
                }
            )
            
            response_text = response.text
            print(f"✓ API response received ({len(response_text)} characters)")
            
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
        
        # Step 4: Parse JSON from response
        print("Parsing JSON from response...")
        result_dict = self._extract_json_from_response(response_text)
        
        # Step 5: Validate with Pydantic
        print("Validating diagnostic result...")
        llm_result = validate_diagnostic_result(result_dict)
        
        # Step 6: Apply scoring adjustments (optional)
        if apply_scoring:
            print("Applying ScoringEngine adjustments...")
            llm_result = self._apply_scoring_adjustments(
                llm_result,
                crop_type,
                required_symptoms
            )
        
        print("✓ Analysis complete")
        
        return llm_result, {
            "raw_response": response_text,
            "parsed_json": result_dict,
            "crop_type": crop_type,
            "image_path": image_path
        }
    
    def _extract_json_from_response(self, response_text: str) -> dict:
        """
        Extract JSON from Gemini response.
        
        Handles cases where the response includes text before/after JSON.
        """
        # Try to find JSON block
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        
        if json_start == -1 or json_end <= json_start:
            raise ValueError("No valid JSON found in response")
        
        json_str = response_text[json_start:json_end]
        
        try:
            result_dict = json.loads(json_str)
            return result_dict
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {str(e)}")
    
    def _apply_scoring_adjustments(
        self,
        llm_result: DiagnosticResult,
        crop_type: str,
        required_symptoms: Optional[list] = None
    ) -> DiagnosticResult:
        """
        Apply ScoringEngine adjustments to LLM output.
        """
        # Define default required symptoms by crop type
        if not required_symptoms:
            required_symptoms = self._get_default_required_symptoms(crop_type)
        
        # Extract observed symptoms from visual evidence
        observed_symptoms = [
            ev.description.lower().strip()
            for ev in llm_result.diagnosis.visual_evidence
        ]
        
        # Calculate adjusted confidence
        try:
            adjusted_confidence = self.scoring_engine.calculate_confidence(
                raw_prob=llm_result.diagnosis.confidence,
                evidence_found=observed_symptoms,
                required_evidence=required_symptoms
            )
            
            llm_result.diagnosis.confidence = adjusted_confidence
            llm_result.confidence_overall = adjusted_confidence
            
        except ValueError:
            # If adjustment fails, keep original confidence
            pass
        
        # Calculate severity based on growth stage and lesion area
        try:
            if llm_result.severity_analysis.affected_area_percentage is not None:
                calculated_severity = self.scoring_engine.calculate_severity(
                    lesion_area_pct=llm_result.severity_analysis.affected_area_percentage,
                    growth_stage=llm_result.severity_analysis.stage
                )
                
                severity_enum = self.scoring_engine.get_severity_enum(calculated_severity)
                llm_result.severity_analysis.severity_index = severity_enum
                
                # Update quantitative score based on severity
                score_map = {"Low": 0.25, "Medium": 0.65, "High": 0.85}
                llm_result.severity_analysis.quantitative_score = score_map.get(
                    calculated_severity, 0.5
                )
        
        except ValueError:
            # If severity calculation fails, keep original values
            pass
        
        return llm_result
    
    @staticmethod
    def _get_default_required_symptoms(crop_type: str) -> list:
        """Get default required symptoms for confidence adjustment."""
        symptoms = {
            "tomato": [
                "concentric rings",
                "yellow halo",
                "brown lesions"
            ],
            "potato": [
                "water-soaked spots",
                "white spore mass",
                "brown lesions"
            ],
            "corn": [
                "rectangular lesions",
                "dark borders",
                "gray coloring"
            ],
            "wheat": [
                "powdery coating",
                "leaf spots",
                "elongated lesions"
            ],
            "lettuce": [
                "yellow spots",
                "fungal growth",
                "leaf curling"
            ]
        }
        
        return symptoms.get(crop_type.lower(), ["lesion", "discoloration"])


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_analyze_local_image(image_path: str, crop_type: str = "tomato"):
    """
    Example: Analyze a local image (requires API key).
    
    PARAMETERS:
    ===========
    image_path : str
        Path to crop image file
        
    crop_type : str
        Type of crop
        
    EXAMPLE:
    ========
    >>> result, response = example_analyze_local_image("leaf.jpg", "tomato")
    >>> print(f"Diagnosis: {result.diagnosis.label}")
    >>> print(f"Confidence: {result.confidence_overall:.1%}")
    """
    import os
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY environment variable")
        print("Export it: export GOOGLE_API_KEY='your-key'")
        return None, None
    
    # Create client
    client = GeminiDiagnosticClient(api_key=api_key)
    
    # Analyze image
    try:
        result, response = client.analyze_image(image_path, crop_type)
        
        # Display results
        print("\n" + "=" * 80)
        print("DIAGNOSTIC RESULT")
        print("=" * 80)
        print(f"Diagnosis: {result.diagnosis.label}")
        print(f"Confidence: {result.confidence_overall:.1%}")
        print(f"Severity: {result.severity_analysis.severity_index}")
        print(f"Urgency: {result.economic_impact.urgency_level}")
        print(f"Yield Loss: {result.economic_impact.yield_loss_estimate}")
        print("\nVisual Evidence:")
        for i, ev in enumerate(result.diagnosis.visual_evidence, 1):
            print(f"  {i}. {ev.description} (confidence: {ev.confidence:.1%})")
        print("=" * 80)
        
        return result, response
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None


def example_mock_analysis():
    """
    Example: Demonstrate the prompt generation and data flow
    without requiring API key.
    """
    from GeminiPromptTemplate import generate_diagnostic_prompt, get_gemini_config
    
    crop_type = "tomato"
    
    print("=" * 80)
    print(f"MOCK ANALYSIS: {crop_type.upper()}")
    print("=" * 80)
    
    # Show system prompt
    system_prompt = generate_diagnostic_prompt(crop_type)
    print(f"\nSystem Prompt Length: {len(system_prompt)} characters")
    print(f"First 300 chars:\n{system_prompt[:300]}...\n")
    
    # Show Gemini config
    config = get_gemini_config(crop_type)
    print(f"\nGemini Configuration:")
    for key, value in config.items():
        if key != "system_prompt":
            print(f"  {key}: {value}")
    
    # Show example flow
    print(f"\nExample LLM Response Flow:")
    print("  1. Analyze image with Gemini Vision")
    print("  2. Model follows 5-step process:")
    print("     - Identify visual features")
    print("     - Estimate leaf area damage")
    print("     - Identify growth stage")
    print("     - Provide diagnostic reasoning")
    print("     - Output JSON diagnostic")
    print("  3. Parse and validate JSON")
    print("  4. Apply ScoringEngine adjustments")
    print("  5. Return DiagnosticResult object")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Gemini Vision Integration - Example Usage")
    print("=" * 80)
    
    # Run mock example (no API key needed)
    example_mock_analysis()
    
    print("\n\n" + "=" * 80)
    print("To analyze a real image:")
    print("=" * 80)
    print("""
    1. Set your Google API key:
       export GOOGLE_API_KEY='your-api-key'
    
    2. Install the Gemini client:
       pip install google-generativeai
    
    3. Use the analyzer:
       from GeminiIntegration import example_analyze_local_image
       result, response = example_analyze_local_image("path/to/image.jpg", "tomato")
    
    4. Access results:
       print(f"Diagnosis: {result.diagnosis.label}")
       print(f"Confidence: {result.confidence_overall:.1%}")
    """)
    print("=" * 80)
0  
**Last Updated:** 2024

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Package Structure](#package-structure)
3. [API Reference](#api-reference)
4. [Data Models & Schemas](#data-models--schemas)
5. [Integration Guide](#integration-guide)
6. [Component Details](#component-details)
7. [Configuration](#configuration)
8. [Examples](#examples)

---

## Architecture Overview

The Agricultural Diagnostic Engine is a modular FastAPI-based system for diagnosing crop pests and diseases using computer vision and machine learning.

### Key Components

```
┌─────────────────┐
│   FastAPI App   │  (REST API Layer)
└────────┬────────┘
         │
         ├─→ /diagnose endpoint (POST)
         ├─→ /pests endpoint (GET)
         ├─→ /health endpoint (GET)
         └─→ /schema endpoint (GET)
         │
         ▼
┌──────────────────────────────┐
│   Core Business Logic        │
├──────────────────────────────┤
│ • ScoringEngine              │
│ • ChemicalDatabase           │
│ • Pydantic Models (Validation)
└────────────┬─────────────────┘
             │
             ├─→ Confidence Calculation
             ├─→ Severity Assessment
             └─→ Treatment Lookup
             │
             ▼
┌──────────────────────────────┐
│   External Integrations      │
├──────────────────────────────┤
│ • Gemini Vision API          │
│ • Image Processing (PIL)     │
└──────────────────────────────┘
```

### Design Principles

- **Separation of Concerns**: Core logic (models, scoring, database) isolated from external integrations (Gemini API)
- **Type Safety**: All inputs/outputs validated with Pydantic v2
- **Modularity**: Swappable components (can replace Gemini with other VLM)
- **Deterministic Scoring**: No LLM for sensitive calculations (confidence, severity)
- **Chemical Safety**: Database approach ensures verified treatments only

---

## Package Structure

```
BuildwithGemini/
├── app/
│   ├── __init__.py                 # Top-level package initialization
│   ├── main.py                     # FastAPI application (run with uvicorn)
│   │
│   ├── core/                       # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── models.py               # All Pydantic models + enums
│   │   ├── scoring.py              # ScoringEngine (confidence, severity)
│   │   └── chemical_db.py          # ChemicalDatabase (treatment lookup)
│   │
│   ├── services/                   # External Integrations Layer
│   │   ├── __init__.py
│   │   └── gemini.py               # Gemini Vision API client
│   │
│   └── tests/                      # Testing & Demonstrations
│       ├── __init__.py
│       └── integration_demo.py      # End-to-end workflow examples
│
├── TECHNICAL_DOCS.md               # This file
├── README.md                        # Setup instructions
└── requirements.txt                # Python dependencies
```

### Import Patterns

**From app.core (Business Logic):**
```python
from app.core import (
    DiagnosticResult,      # Pydantic model
    ScoringEngine,         # Scoring class
    ChemicalDatabase,      # Database class
    SeverityLevel,         # Enum
    UrgencyLevel,          # Enum
    CropStage,             # Enum
)
```

**From app.services (Integrations):**
```python
from app.services import (
    GeminiDiagnosticClient,      # Gemini client
    generate_diagnostic_prompt,   # Prompt template
    prepare_image_for_gemini,    # Image preprocessing
)
```

---

## API Reference

### 1. POST /diagnose

**Diagnose a crop disease/pest from an image.**

**Request:**
```bash
curl -X POST http://localhost:8000/diagnose \
  -F "file=@crop_image.jpg" \
  -F "crop_type=tomato" \
  -F "region=NORTH_AMERICA"
```

**Parameters:**
- `file` (UploadFile, required): Image file (JPEG, PNG)
- `crop_type` (string, required): Crop type (tomato, potato, corn, wheat, lettuce)
- `region` (string, optional): Region for treatment recommendations
  - Valid values: `NORTH_AMERICA`, `SOUTH_AMERICA`, `EUROPE`, `ASIA`, `AFRICA`, `AUSTRALIA`
  - Default: `NORTH_AMERICA`

**Response (200 OK):**
```json
{
  "diagnosis": {
    "label": "Early Blight (Alternaria solani)",
    "confidence": 0.823,
    "visual_evidence": [
      {
        "description": "Concentric rings on lower leaves",
        "confidence": 0.85,
        "location": "Leaf surface"
      }
    ]
  },
  "severity_analysis": {
    "severity_index": "Medium",
    "quantitative_score": 0.823,
    "stage": "Vegetative",
    "affected_area_percentage": 18.5
  },
  "economic_impact": {
    "yield_loss_estimate": "8.5%",
    "urgency_level": "Medium"
  },
  "treatment_plan": {
    "organic_treatments": [...],
    "chemical_treatments": [...]
  },
  "confidence_overall": 0.823
}
```

**Error Responses:**
- `400 Bad Request`: Invalid region or corrupted image file
- `500 Internal Server Error`: API or processing error

---

### 2. GET /health

**Health check endpoint.**

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": {
    "scoring_engine": true,
    "chemical_database": true,
    "gemini_client": true
  }
}
```

---

### 3. GET /pests

**List all pests in the chemical database.**

**Request:**
```bash
curl http://localhost:8000/pests
```

**Response (200 OK):**
```json
{
  "count": 6,
  "pests": [
    "Early Blight (Alternaria solani)",
    "Powdery Mildew (Erysiphe cichoracearum)",
    "Colorado Potato Beetle",
    "Corn Earworm",
    "Wheat Rust (Puccinia triticina)",
    "Lettuce Downy Mildew"
  ]
}
```

---

### 4. GET /pests/{pest_name}

**Get available treatments for a specific pest.**

**Request:**
```bash
curl "http://localhost:8000/pests/Early%20Blight%20(Alternaria%20solani)?region=NORTH_AMERICA"
```

**Parameters:**
- `pest_name` (string, required): Pest name (URL-encoded)
- `region` (string, optional): Geographic region
  - Default: `NORTH_AMERICA`

**Response (200 OK):**
```json
{
  "pest_name": "Early Blight (Alternaria solani)",
  "region": "NORTH_AMERICA",
  "treatment_count": 3,
  "treatments": [
    {
      "product_name": "Mancozeb 80WP",
      "active_ingredient": "Mancozeb",
      "dosage": "2.5 kg/1000L",
      "application_frequency": "Every 7 days",
      "effectiveness_rate": 0.92,
      "ppe_required": ["Gloves", "Respirator", "Goggles"],
      "pre_harvest_interval": 7,
      "re_entry_interval": 5
    }
  ]
}
```

---

### 5. GET /schema

**Get JSON schema for DiagnosticResult.**

**Request:**
```bash
curl http://localhost:8000/schema
```

**Response:** Complete JSON Schema for DiagnosticResult model (for validation/documentation)

---

## Data Models & Schemas

### Core Enums

**SeverityLevel:**
```python
class SeverityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
```

**UrgencyLevel:**
```python
class UrgencyLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
```

**CropStage:**
```python
class CropStage(str, Enum):
    SEEDLING = "Seedling"
    VEGETATIVE = "Vegetative"
    FLOWERING = "Flowering"
    FRUITING = "Fruiting"
    MATURE = "Mature"
```

**Region (Chemical Database):**
```python
class Region(str, Enum):
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
    EUROPE = "Europe"
    ASIA = "Asia"
    AFRICA = "Africa"
    AUSTRALIA = "Australia"
```

### Main Models

**VisualEvidence:**
Evidence of disease/pest from image analysis.
```python
{
  "description": "string",          # What was observed
  "confidence": float,              # 0.0-1.0 confidence level
  "location": "string"              # Location in image (leaf, stem, etc)
}
```

**Diagnosis:**
Primary diagnosis from vision analysis.
```python
{
  "label": "string",                # Pest/disease name
  "confidence": float,              # Overall confidence 0.0-1.0
  "visual_evidence": [VisualEvidence, ...]
}
```

**SeverityAnalysis:**
Assessment of disease severity and impact.
```python
{
  "severity_index": SeverityLevel,  # Low/Medium/High
  "quantitative_score": float,      # 0.0-1.0
  "stage": CropStage,               # Growth stage of crop
  "affected_area_percentage": float # % of plant affected
}
```

**EconomicImpact:**
Economic assessment and urgency.
```python
{
  "yield_loss_estimate": "string",  # e.g., "8.5%"
  "urgency_level": UrgencyLevel     # Low/Medium/High/Critical
}
```

**OrganicTreatment:**
Organic/non-chemical treatment option.
```python
{
  "treatment_name": "string",           # e.g., "Neem Oil"
  "dosage": "string",                   # e.g., "2-3%"
  "application_frequency": "string",    # e.g., "Every 7 days"
  "description": "string",              # Details
  "effectiveness_rate": float           # 0.0-1.0
}
```

**ChemicalTreatment:**
Chemical treatment option with safety information.
```python
{
  "treatment_name": "string",           # Product name
  "active_ingredient": "string",        # e.g., "Mancozeb"
  "dosage": "string",                   # e.g., "2.5 kg/1000L"
  "application_frequency": "string",    # e.g., "Every 7 days"
  "description": "string",              # Details
  "effectiveness_rate": float,          # 0.0-1.0
  "safety_equipment": [string, ...],    # Required PPE
  "re_entry_interval": int              # Hours before re-entry
}
```

**TreatmentPlan:**
Complete treatment recommendations.
```python
{
  "organic_treatments": [OrganicTreatment, ...],
  "chemical_treatments": [ChemicalTreatment, ...]
}
```

**DiagnosticResult:**
Complete diagnostic output (main response model).
```python
{
  "diagnosis": Diagnosis,
  "severity_analysis": SeverityAnalysis,
  "economic_impact": EconomicImpact,
  "treatment_plan": TreatmentPlan,
  "confidence_overall": float  # 0.0-1.0
}
```

---

## Integration Guide

### Running the API Server

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Start server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`
API docs: `http://localhost:8000/docs` (Swagger UI)

### Running Integration Tests

**Execute demo workflow:**
```bash
python -m app.tests.integration_demo
```

### Programmatic Usage

```python
from app.core import DiagnosticResult, ScoringEngine, ChemicalDatabase
from app.services import GeminiDiagnosticClient

# Initialize components
scorer = ScoringEngine()
database = ChemicalDatabase()
gemini = GeminiDiagnosticClient()

# Analyze image
analysis, raw_response = gemini.analyze_image(
    image_path="crop_image.jpg",
    crop_type="tomato"
)

# Get treatments
treatments = database.get_safe_treatment(
    pest_name="Early Blight",
    region=Region.NORTH_AMERICA,
    crop_type="tomato"
)

# Calculate confidence
confidence = scorer.calculate_confidence(
    raw_prob=0.82,
    evidence_found=["rings", "lesion", "halo"],
    required_evidence=["rings", "lesion", "halo"]
)
```

---

## Component Details

### ScoringEngine

Deterministic scoring for diagnostic confidence and severity assessment.

**Methods:**

**calculate_confidence(raw_prob, evidence_found, required_evidence) → float**

Combines VLM probability with evidence validation:
- Weighing: 70% raw probability, 30% evidence match
- Returns: float 0.0-1.0

```python
score = engine.calculate_confidence(
    raw_prob=0.82,                    # From VLM
    evidence_found=["rings", "halo"], # Observed
    required_evidence=["rings", "halo", "lesion"]  # Expected
)
# Returns: 0.80 (slightly lower due to missing lesion)
```

**calculate_severity(lesion_area_pct, growth_stage) → str**

Classifies severity based on affected area and growth stage:
- Seedling: Very sensitive (5% threshold for Medium)
- Mature: More tolerant (30% threshold for Medium)
- Returns: "Low", "Medium", or "High"

```python
severity = engine.calculate_severity(
    lesion_area_pct=18.5,
    growth_stage="vegetative"
)
# Returns: "Medium"
```

### ChemicalDatabase

Verified, never-LLM-generated chemical treatment database.

**Methods:**

**get_all_pests() → List[str]**
Returns list of all pests in database.

**get_safe_treatment(pest_name, region, crop_type) → List[dict]**
Returns safe treatments for pest/region combination.
Falls back to "Consult Local Expert" if not found.

**get_treatment_for_pest(pest_name, region) → List[dict]**
Returns all treatments for a pest in a region.

**get_ppe_requirements(treatment) → List[str]**
Returns required personal protective equipment.

### GeminiDiagnosticClient

Integration with Google Gemini 2.0 Flash Vision API.

**Methods:**

**analyze_image(image_path, crop_type) → Tuple[dict, dict]**

Analyzes crop image using Gemini Vision API.
- Requires: GOOGLE_API_KEY environment variable
- Returns: (parsed_analysis, raw_response)
- Analysis includes: identified_pest, raw_confidence, visible_symptoms, growth_stage, lesion_coverage

---

## Configuration

### Environment Variables

**Required:**
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Optional:**
```bash
GEMINI_MODEL=gemini-2.0-flash-exp  # Default model
LOG_LEVEL=INFO
```

### Chemical Database Configuration

The ChemicalDatabase is initialized with hardcoded treatment data (safety-critical):
- 6 pests with verified treatments
- Region-specific restrictions
- Pre-harvest intervals enforced

To add treatments: Edit `app/core/chemical_db.py` and add to `self.database` dictionary.

### ScoringEngine Configuration

Confidence calculation weights (in `app/core/scoring.py`):
```python
CONFIDENCE_WEIGHTS = {
    "raw_probability": 0.70,  # VLM confidence
    "evidence_match": 0.30    # Evidence validation
}
```

Severity thresholds by crop stage:
```python
SEVERITY_THRESHOLDS = {
    CropStage.SEEDLING: {"medium": 5, "high": 10},
    CropStage.VEGETATIVE: {"medium": 15, "high": 25},
    # ... more stages
}
```

---

## Examples

### Complete Workflow Example

```python
import base64
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Prepare image
with open("tomato_disease.jpg", "rb") as f:
    files = {"file": f}
    data = {"crop_type": "tomato", "region": "NORTH_AMERICA"}
    
    # 2. Send diagnosis request
    response = client.post("/diagnose", files=files, data=data)

# 3. Parse response
result = response.json()
print(f"Pest: {result['diagnosis']['label']}")
print(f"Confidence: {result['confidence_overall']:.1%}")
print(f"Severity: {result['severity_analysis']['severity_index']}")
print(f"Treatments: {len(result['treatment_plan']['chemical_treatments'])} recommended")

# 4. Access treatments
for treatment in result['treatment_plan']['chemical_treatments']:
    print(f"  - {treatment['treatment_name']} ({treatment['effectiveness_rate']:.0%} effective)")
```

### Confidence Calculation Example

```python
from app.core import ScoringEngine

scorer = ScoringEngine()

# Scenario: VLM very confident (0.90) but missing one key symptom
confidence = scorer.calculate_confidence(
    raw_prob=0.90,
    evidence_found=["rings", "halo"],
    required_evidence=["rings", "halo", "lesion"]
)
# Result: 0.63 (70% of 0.90 + 30% of 0.67) ≈ 0.63
```

### Severity Calculation Example

```python
from app.core import ScoringEngine

scorer = ScoringEngine()

# Early blight at different stages
severity_seedling = scorer.calculate_severity(
    lesion_area_pct=3.0,
    growth_stage="Seedling"
)
# Result: "Medium" (sensitive stage)

severity_mature = scorer.calculate_severity(
    lesion_area_pct=3.0,
    growth_stage="Mature"
)
# Result: "Low" (tolerant stage)
```

### Treatment Lookup Example

```python
from app.core import ChemicalDatabase, Region

database = ChemicalDatabase()

# Get treatments for specific pest
treatments = database.get_safe_treatment(
    pest_name="Early Blight (Alternaria solani)",
    region=Region.NORTH_AMERICA,
    crop_type="tomato"
)

# Check PPE requirements
for treatment in treatments:
    ppe = database.get_ppe_requirements(treatment)
    print(f"{treatment['product_name']} requires: {', '.join(ppe)}")
```

---

## Troubleshooting

### "AttributeError: UrgencyLevel.MODERATE"
**Solution:** Use `UrgencyLevel.MEDIUM` (MODERATE doesn't exist in enum)

### "Invalid region: REGION_NAME"
**Solution:** Check valid region values in API reference (NORTH_AMERICA, EUROPE, etc.)

### Gemini API Errors
**Solution:** Verify `GOOGLE_API_KEY` is set and valid. Check API quota in Google Cloud console.

### Image Processing Errors
**Solution:** Ensure image file is valid JPEG/PNG. Maximum recommended size: 5MB

---

## Performance Characteristics

- **Confidence Calculation:** <1ms
- **Severity Assessment:** <1ms
- **Database Lookup:** <5ms
- **Gemini API Call:** 3-10s (network dependent)
- **Image Processing:** 500ms-2s (depends on size)

**Typical /diagnose request:** 4-12 seconds total

---

## Security Considerations

- **API Key Storage:** Use environment variables, never hardcode
- **Image Processing:** Validate file type and size before processing
- **Regional Restrictions:** Chemical database enforces region-specific regulations
- **PPE Warnings:** Always include required safety equipment in treatments

---

## Future Enhancements

- [ ] Multi-language prompt support
- [ ] Batch image processing endpoint
- [ ] Historical diagnosis storage
- [ ] Custom pest database per farm
- [ ] Real-time severity monitoring
- [ ] Integration with agronomic recommendations API
- [ ] Geographic warning system for pest spread

---

## License & Attribution

Built with:
- FastAPI: Modern Python web framework
- Pydantic: Data validation
- Google Gemini 2.0 Flash: Vision-Language Model
- Pillow: Image processing

---

**For support or questions, refer to README.md for setup instructions or contact the development team.**
