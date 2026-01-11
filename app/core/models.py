"""
Agricultural Diagnostic Engine - Data Models

All Pydantic models and enums for strict JSON schema validation.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMERATIONS
# ============================================================================

class SeverityLevel(str, Enum):
    """Defines severity levels for pest/disease diagnosis."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class CropStage(str, Enum):
    """Defines the growth stage of the crop."""
    GERMINATION = "Germination"
    VEGETATIVE = "Vegetative"
    FLOWERING = "Flowering"
    FRUITING = "Fruiting"
    MATURITY = "Maturity"


class UrgencyLevel(str, Enum):
    """Defines the urgency of treatment action."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# ============================================================================
# CORE MODELS
# ============================================================================

class VisualEvidence(BaseModel):
    """Single piece of visual evidence from image analysis."""
    description: str = Field(
        ...,
        description="Description of the visual evidence observed",
        min_length=10,
        max_length=500
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)"
    )
    location: Optional[str] = Field(
        None,
        description="Spatial location in image",
        max_length=100
    )


class Diagnosis(BaseModel):
    """Primary diagnosis result for pest or disease."""
    label: str = Field(
        ...,
        description="Name of pest/disease",
        min_length=3,
        max_length=200
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in diagnosis"
    )
    visual_evidence: List[VisualEvidence] = Field(
        ...,
        description="Supporting visual evidence",
        min_items=1
    )


class SeverityAnalysis(BaseModel):
    """Analyzes severity and progression stage."""
    severity_index: SeverityLevel = Field(
        ...,
        description="Categorical severity: Low, Medium, High"
    )
    quantitative_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Numerical severity (0.0-1.0)"
    )
    stage: str = Field(
        ...,
        description="Development stage",
        min_length=3,
        max_length=100
    )
    affected_area_percentage: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Affected area %"
    )


class EconomicImpact(BaseModel):
    """Quantifies economic impact."""
    yield_loss_estimate: str = Field(
        ...,
        description="Yield loss estimate",
        max_length=50
    )
    urgency_level: UrgencyLevel = Field(
        ...,
        description="Treatment urgency"
    )
    estimated_cost_impact: Optional[str] = Field(
        None,
        description="Cost impact estimate",
        max_length=100
    )
    days_to_critical: Optional[int] = Field(
        None,
        ge=0,
        description="Days until critical"
    )


class OrganicTreatment(BaseModel):
    """Organic treatment recommendation."""
    treatment_name: str = Field(
        ...,
        description="Treatment name",
        min_length=3,
        max_length=150
    )
    dosage: str = Field(
        ...,
        description="Dosage/concentration",
        max_length=100
    )
    application_frequency: str = Field(
        ...,
        description="Application frequency",
        max_length=100
    )
    description: str = Field(
        ...,
        description="Detailed description",
        min_length=20,
        max_length=500
    )
    effectiveness_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Effectiveness rate"
    )
    precautions: Optional[str] = Field(
        None,
        description="Safety precautions",
        max_length=300
    )


class ChemicalTreatment(BaseModel):
    """Chemical treatment with safety requirements."""
    treatment_name: str = Field(
        ...,
        description="Chemical product name",
        min_length=3,
        max_length=150
    )
    active_ingredient: str = Field(
        ...,
        description="Active ingredient",
        max_length=200
    )
    dosage: str = Field(
        ...,
        description="Application dosage",
        max_length=100
    )
    application_frequency: str = Field(
        ...,
        description="Application frequency",
        max_length=100
    )
    description: str = Field(
        ...,
        description="Detailed description",
        min_length=20,
        max_length=500
    )
    effectiveness_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Effectiveness rate"
    )
    safety_equipment: List[str] = Field(
        ...,
        description="Required PPE",
        min_items=1
    )
    re_entry_interval: str = Field(
        ...,
        description="Re-entry interval",
        max_length=50
    )
    environmental_notes: Optional[str] = Field(
        None,
        description="Environmental impact notes",
        max_length=300
    )


class TreatmentPlan(BaseModel):
    """Complete treatment plan with organic and chemical options."""
    organic_treatments: List[OrganicTreatment] = Field(
        ...,
        description="Organic options",
        min_items=0
    )
    chemical_treatments: List[ChemicalTreatment] = Field(
        ...,
        description="Chemical options",
        min_items=0
    )
    integrated_approach: Optional[str] = Field(
        None,
        description="IPM strategy",
        max_length=500
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes",
        max_length=500
    )

    @field_validator("organic_treatments", "chemical_treatments")
    @classmethod
    def at_least_one_treatment(cls, v):
        """Ensure at least one treatment provided."""
        if not v:
            raise ValueError("At least one treatment (organic or chemical) required")
        return v


class DiagnosticResult(BaseModel):
    """Complete diagnostic result from the engine."""
    diagnosis: Diagnosis = Field(
        ...,
        description="Primary diagnosis"
    )
    severity_analysis: SeverityAnalysis = Field(
        ...,
        description="Severity analysis"
    )
    economic_impact: EconomicImpact = Field(
        ...,
        description="Economic impact"
    )
    treatment_plan: TreatmentPlan = Field(
        ...,
        description="Treatment recommendations"
    )
    additional_recommendations: Optional[str] = Field(
        None,
        description="Expert recommendations",
        max_length=500
    )
    confidence_overall: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_diagnostic_result(data: dict) -> DiagnosticResult:
    """Validate dictionary against DiagnosticResult schema."""
    try:
        return DiagnosticResult(**data)
    except Exception as e:
        raise ValueError(f"Validation failed: {str(e)}")


def get_schema_json() -> dict:
    """Get JSON schema for DiagnosticResult."""
    return DiagnosticResult.model_json_schema()
