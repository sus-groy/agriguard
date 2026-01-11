"""
Agricultural Diagnostic Engine - Core Business Logic

Centralizes all models, enums, and core logic:
- models: Pydantic data structures
- scoring: Confidence and severity calculations
- chemical_db: Verified chemical treatment database
"""

from .models import (
    # Enums
    SeverityLevel,
    CropStage,
    UrgencyLevel,
    # Models
    VisualEvidence,
    Diagnosis,
    SeverityAnalysis,
    EconomicImpact,
    OrganicTreatment,
    ChemicalTreatment,
    TreatmentPlan,
    DiagnosticResult,
    # Functions
    validate_diagnostic_result,
    get_schema_json,
)

from .scoring import ScoringEngine
from .chemical_db import ChemicalDatabase, Region

__all__ = [
    # Enums
    "SeverityLevel",
    "CropStage",
    "UrgencyLevel",
    # Models
    "VisualEvidence",
    "Diagnosis",
    "SeverityAnalysis",
    "EconomicImpact",
    "OrganicTreatment",
    "ChemicalTreatment",
    "TreatmentPlan",
    "DiagnosticResult",
    # Functions
    "validate_diagnostic_result",
    "get_schema_json",
    # Classes
    "ScoringEngine",
    "ChemicalDatabase",
    "Region",
]
