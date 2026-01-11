"""
FastAPI REST API for Agricultural Diagnostic Engine

Endpoints:
  POST   /diagnose       - Analyze crop image and return diagnosis
  GET    /health         - Health check
  GET    /pests          - List all pests in database
  GET    /pests/{name}   - Get treatments for specific pest

Run: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.testclient import TestClient
from typing import List, Optional
from PIL import Image
import io
import base64

from app.core import (
    DiagnosticResult,
    Diagnosis,
    SeverityAnalysis,
    EconomicImpact,
    VisualEvidence,
    OrganicTreatment,
    ChemicalTreatment,
    TreatmentPlan,
    ScoringEngine,
    ChemicalDatabase,
    Region,
    SeverityLevel,
    UrgencyLevel,
    CropStage,
    get_schema_json,
)
from app.services import (
    GeminiDiagnosticClient,
    generate_diagnostic_prompt,
)


app = FastAPI(
    title="Agricultural Diagnostic Engine",
    description="AI-powered pest and disease diagnosis for crops",
    version="1.0.0"
)

# Initialize components
scoring_engine = ScoringEngine()
chemical_db = ChemicalDatabase()
gemini_client = GeminiDiagnosticClient()


# ============================================================================
# DATA MODELS FOR API
# ============================================================================

class DiagnoseRequest:
    """Request body for /diagnose endpoint"""
    crop_type: str
    image: UploadFile
    region: Optional[str] = "NORTH_AMERICA"


class PestTreatmentResponse:
    """Response for /pests/{name} endpoint"""
    pest_name: str
    treatments: List[dict]
    available_regions: List[str]


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "models_loaded": {
            "scoring_engine": True,
            "chemical_database": True,
            "gemini_client": True,
        }
    }


# ============================================================================
# PEST DATABASE ENDPOINTS
# ============================================================================

@app.get("/pests")
async def list_pests():
    """List all pests in chemical database."""
    pests = chemical_db.get_all_pests()
    return {
        "count": len(pests),
        "pests": pests
    }


@app.get("/pests/{pest_name}")
async def get_pest_treatments(pest_name: str, region: str = "NORTH_AMERICA"):
    """Get available treatments for a specific pest."""
    try:
        region_enum = Region[region]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid region: {region}. Valid options: {[r.name for r in Region]}"
        )
    
    treatments = chemical_db.get_treatment_for_pest(pest_name, region_enum)
    
    if not treatments:
        return {
            "pest_name": pest_name,
            "region": region,
            "treatments": [],
            "message": "No treatments found. Consult local agricultural expert."
        }
    
    return {
        "pest_name": pest_name,
        "region": region,
        "treatment_count": len(treatments),
        "treatments": treatments
    }


# ============================================================================
# MAIN DIAGNOSTIC ENDPOINT
# ============================================================================

@app.post("/diagnose")
async def diagnose_crop(crop_type: str, file: UploadFile = File(...), region: str = "NORTH_AMERICA"):
    """
    Analyze crop image and return complete diagnostic result.
    
    Parameters:
        crop_type: Type of crop (tomato, potato, corn, wheat, lettuce)
        file: Image file upload
        region: Geographic region for treatment recommendations
    
    Returns:
        DiagnosticResult with diagnosis, severity, treatments, and confidence
    """
    
    # Validate region
    try:
        region_enum = Region[region]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid region: {region}"
        )
    
    # Read and validate image
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image.verify()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    # Convert to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # ========================================================================
    # STEP 1: Call Vision Language Model (Mock)
    # ========================================================================
    
    vlm_analysis = {
        "crop": crop_type,
        "identified_pest": "Early Blight (Alternaria solani)",
        "raw_confidence": 0.82,
        "visible_symptoms": [
            "Concentric rings on lower leaves",
            "Brown necrotic lesions",
            "Yellow halo around lesions"
        ],
        "growth_stage": "vegetative",
        "lesion_coverage_percent": 18.5,
    }
    
    # ========================================================================
    # STEP 2: Recalculate with ScoringEngine
    # ========================================================================
    
    evidence_found = vlm_analysis['visible_symptoms']
    required_evidence = ["necrotic lesion", "characteristic rings", "discoloration"]
    
    recalculated_confidence = scoring_engine.calculate_confidence(
        raw_prob=vlm_analysis['raw_confidence'],
        evidence_found=evidence_found,
        required_evidence=required_evidence
    )
    
    recalculated_severity = scoring_engine.calculate_severity(
        lesion_area_pct=vlm_analysis['lesion_coverage_percent'],
        growth_stage=vlm_analysis['growth_stage']
    )
    
    # ========================================================================
    # STEP 3: Lookup ChemicalDatabase
    # ========================================================================
    
    pest_name = vlm_analysis['identified_pest']
    treatments = chemical_db.get_safe_treatment(
        pest_name,
        region_enum,
        crop_type
    )
    
    # ========================================================================
    # STEP 4: Build DiagnosticResult
    # ========================================================================
    
    evidence_list = [
        VisualEvidence(
            description=symptom,
            confidence=0.85,
            location="Leaf surface"
        )
        for symptom in evidence_found
    ]
    
    diagnosis = Diagnosis(
        label=pest_name,
        confidence=recalculated_confidence,
        visual_evidence=evidence_list
    )
    
    # Create treatment list
    organic_treatments = [
        OrganicTreatment(
            treatment_name="Neem Oil Spray",
            dosage="2-3%",
            application_frequency="Every 7 days",
            description="Natural oil spray effective against fungal diseases",
            effectiveness_rate=0.65
        ),
    ]
    
    chemical_treatments = []
    for db_treatment in treatments:
        # Convert PPE dict to list
        ppe_list = []
        ppe_dict = db_treatment.get('ppe_required', {})
        
        if isinstance(ppe_dict, dict):
            # If it's a dict from PPERequirement, convert to list
            if ppe_dict.get('gloves') and ppe_dict.get('gloves') != "None":
                ppe_list.append(f"Gloves ({ppe_dict['gloves']})")
            if ppe_dict.get('respirator') and ppe_dict.get('respirator') != "None":
                ppe_list.append(f"Respirator ({ppe_dict['respirator']})")
            if ppe_dict.get('eye_protection') and ppe_dict.get('eye_protection') != "None":
                ppe_list.append(f"Eye protection ({ppe_dict['eye_protection']})")
            if ppe_dict.get('clothing') and ppe_dict.get('clothing') != "None":
                ppe_list.append(ppe_dict['clothing'])
            if ppe_dict.get('boots') and ppe_dict.get('boots') != "None":
                ppe_list.append(ppe_dict['boots'])
        elif isinstance(ppe_dict, list):
            # Already a list
            ppe_list = ppe_dict
        
        if not ppe_list:
            ppe_list = ["Standard safety precautions"]
        
        chem = ChemicalTreatment(
            treatment_name=db_treatment['product_name'],
            active_ingredient=db_treatment['active_ingredient'],
            dosage=db_treatment['dosage'],
            application_frequency=db_treatment['application_frequency'],
            description=f"Pre-harvest interval: {db_treatment['pre_harvest_interval']} days",
            effectiveness_rate=db_treatment['effectiveness_rate'],
            safety_equipment=ppe_list,
            re_entry_interval=str(db_treatment.get('re_entry_interval', '48 hours')),
        )
        chemical_treatments.append(chem)
    
    treatment_plan = TreatmentPlan(
        organic_treatments=organic_treatments,
        chemical_treatments=chemical_treatments,
    )
    
    severity_analysis = SeverityAnalysis(
        severity_index=SeverityLevel[recalculated_severity.upper()],
        quantitative_score=recalculated_confidence,
        stage=CropStage.VEGETATIVE,
        affected_area_percentage=vlm_analysis['lesion_coverage_percent']
    )
    
    economic_impact = EconomicImpact(
        yield_loss_estimate=f"{vlm_analysis['lesion_coverage_percent']:.1f}%",
        urgency_level=UrgencyLevel.MEDIUM
    )
    
    diagnostic_result = DiagnosticResult(
        diagnosis=diagnosis,
        severity_analysis=severity_analysis,
        economic_impact=economic_impact,
        treatment_plan=treatment_plan,
        confidence_overall=recalculated_confidence
    )
    
    return diagnostic_result.model_dump()


# ============================================================================
# SCHEMA ENDPOINT
# ============================================================================

@app.get("/schema")
async def get_schema():
    """Get JSON schema for DiagnosticResult."""
    return get_schema_json()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# Test client for easy testing
def get_test_client():
    """Get TestClient for testing endpoints."""
    return TestClient(app)


if __name__ == "__main__":
    # Example test
    client = get_test_client()
    
    # Test health
    print("Testing /health endpoint...")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # Test pests list
    print("Testing /pests endpoint...")
    response = client.get("/pests")
    print(f"Status: {response.status_code}")
    pests_data = response.json()
    print(f"Found {pests_data['count']} pests\n")
    
    # Test get specific pest
    if pests_data['count'] > 0:
        first_pest = pests_data['pests'][0]
        print(f"Testing /pests/{{name}} for {first_pest}...")
        response = client.get(f"/pests/{first_pest}")
        print(f"Status: {response.status_code}")
        print(f"Treatments: {response.json()['treatment_count']}\n")
