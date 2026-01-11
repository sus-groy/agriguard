"""
Agricultural Diagnostic Engine - Scoring Engine

Deterministic scoring for confidence and severity assessment.
"""

from enum import Enum
from typing import List
from .models import SeverityLevel, CropStage


class GrowthStageSensitivity(str, Enum):
    """Sensitivity of growth stage to damage."""
    VERY_SENSITIVE = "very_sensitive"
    SENSITIVE = "sensitive"
    MODERATE = "moderate"
    TOLERANT = "tolerant"
    VERY_TOLERANT = "very_tolerant"


# Confidence calculation weights
CONFIDENCE_WEIGHTS = {
    "raw_probability": 0.70,
    "evidence_completeness": 0.30
}

# Severity thresholds by stage
SEVERITY_THRESHOLDS = {
    GrowthStageSensitivity.VERY_SENSITIVE: (5.0, 10.0, 15.0),
    GrowthStageSensitivity.SENSITIVE: (10.0, 20.0, 35.0),
    GrowthStageSensitivity.MODERATE: (15.0, 30.0, 50.0),
    GrowthStageSensitivity.TOLERANT: (20.0, 40.0, 60.0),
    GrowthStageSensitivity.VERY_TOLERANT: (30.0, 50.0, 75.0),
}

# Growth stage mapping
STAGE_SENSITIVITY_MAP = {
    CropStage.GERMINATION: GrowthStageSensitivity.VERY_SENSITIVE,
    CropStage.VEGETATIVE: GrowthStageSensitivity.SENSITIVE,
    CropStage.FLOWERING: GrowthStageSensitivity.MODERATE,
    CropStage.FRUITING: GrowthStageSensitivity.TOLERANT,
    CropStage.MATURITY: GrowthStageSensitivity.VERY_TOLERANT,
}

STRING_STAGE_SENSITIVITY_MAP = {
    "germination": GrowthStageSensitivity.VERY_SENSITIVE,
    "seedling": GrowthStageSensitivity.VERY_SENSITIVE,
    "vegetative": GrowthStageSensitivity.SENSITIVE,
    "early flowering": GrowthStageSensitivity.MODERATE,
    "flowering": GrowthStageSensitivity.MODERATE,
    "fruit set": GrowthStageSensitivity.TOLERANT,
    "fruiting": GrowthStageSensitivity.TOLERANT,
    "fruit development": GrowthStageSensitivity.TOLERANT,
    "mature": GrowthStageSensitivity.VERY_TOLERANT,
    "pre-harvest": GrowthStageSensitivity.VERY_TOLERANT,
}


class ScoringEngine:
    """Deterministic scoring engine for diagnostics."""

    @staticmethod
    def calculate_confidence(
        raw_prob: float,
        evidence_found: List[str],
        required_evidence: List[str]
    ) -> float:
        """
        Calculate confidence using weighted average.
        
        Formula: confidence = (raw_prob × 0.70) + (evidence_completeness × 0.30)
        
        :param raw_prob: Model probability (0.0-1.0)
        :param evidence_found: Observed symptoms
        :param required_evidence: Expected symptoms
        :return: Adjusted confidence (0.0-1.0)
        """
        if not 0.0 <= raw_prob <= 1.0:
            raise ValueError(f"raw_prob must be 0.0-1.0, got {raw_prob}")
        
        if not required_evidence:
            raise ValueError("required_evidence cannot be empty")
        
        # Calculate evidence completeness
        evidence_found_set = set(e.lower().strip() for e in evidence_found)
        required_evidence_set = set(e.lower().strip() for e in required_evidence)
        matches = len(evidence_found_set & required_evidence_set)
        evidence_completeness = matches / len(required_evidence)
        
        # Weighted confidence
        confidence = (raw_prob * CONFIDENCE_WEIGHTS["raw_probability"]) + \
                     (evidence_completeness * CONFIDENCE_WEIGHTS["evidence_completeness"])
        
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def _get_growth_stage_sensitivity(growth_stage: str) -> GrowthStageSensitivity:
        """Map growth stage to sensitivity level."""
        stage_lower = growth_stage.lower().strip()
        
        if stage_lower in STRING_STAGE_SENSITIVITY_MAP:
            return STRING_STAGE_SENSITIVITY_MAP[stage_lower]
        
        try:
            crop_stage = CropStage[growth_stage.upper()]
            return STAGE_SENSITIVITY_MAP.get(crop_stage, GrowthStageSensitivity.MODERATE)
        except KeyError:
            raise ValueError(f"Unknown growth stage: {growth_stage}")

    @staticmethod
    def calculate_severity(lesion_area_pct: float, growth_stage: str) -> str:
        """
        Calculate severity based on lesion area and growth stage.
        
        :param lesion_area_pct: Affected area percentage (0.0-100.0)
        :param growth_stage: Growth stage string
        :return: "Low", "Medium", or "High"
        """
        if not 0.0 <= lesion_area_pct <= 100.0:
            raise ValueError(f"lesion_area_pct must be 0.0-100.0, got {lesion_area_pct}")
        
        sensitivity = ScoringEngine._get_growth_stage_sensitivity(growth_stage)
        low_thresh, med_thresh, high_thresh = SEVERITY_THRESHOLDS[sensitivity]
        
        if lesion_area_pct <= low_thresh:
            return "Low"
        elif lesion_area_pct <= med_thresh:
            return "Medium"
        else:
            return "High"

    @staticmethod
    def get_severity_enum(severity_str: str) -> SeverityLevel:
        """Convert severity string to enum."""
        mapping = {
            "Low": SeverityLevel.LOW,
            "Medium": SeverityLevel.MEDIUM,
            "High": SeverityLevel.HIGH,
        }
        
        if severity_str not in mapping:
            raise ValueError(f"Invalid severity: {severity_str}")
        
        return mapping[severity_str]
