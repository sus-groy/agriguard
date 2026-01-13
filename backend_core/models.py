"""
Data models for The Specialist agricultural diagnostic system.
Uses dataclasses for strict schema validation and type safety.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class SeverityLevel(Enum):
    """Pest/disease severity classification"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TreatmentType(Enum):
    """Type of treatment intervention"""
    ORGANIC = "Organic"
    CHEMICAL = "Chemical"
    BIOLOGICAL = "Biological"
    CULTURAL = "Cultural"
    MECHANICAL = "Mechanical"


class GrowthStage(Enum):
    """Crop growth stages"""
    SEEDLING = "Seedling"
    VEGETATIVE = "Vegetative"
    FLOWERING = "Flowering"
    FRUITING = "Fruiting"
    HARVEST = "Harvest"


@dataclass
class DiagnosticInput:
    """Input data from visual detection system"""
    pest_name: str
    confidence: float  # 0.0 to 1.0
    lesion_percentage: float  # % of affected area
    growth_stage: GrowthStage
    crop_type: str
    crop_value_per_hectare: float  # in INR
    location: str
    detection_timestamp: datetime = field(default_factory=datetime.now)
    visual_symptoms: List[str] = field(default_factory=list)


@dataclass
class SeverityAnalysis:
    """Analysis of pest/disease severity"""
    severity_level: SeverityLevel
    affected_area_pct: float
    confidence_score: float
    risk_factors: List[str]
    progression_rate: str  # "Slow", "Moderate", "Rapid"
    reasoning: str


@dataclass
class ChemicalTreatment:
    """Chemical intervention details"""
    product_name: str
    active_ingredient: str
    dosage: str
    application_method: str
    rei_hours: int  # Re-Entry Interval
    phi_days: int  # Pre-Harvest Interval
    ppe_required: List[str]
    cost_per_hectare: float
    approved_regions: List[str]
    toxicity_class: str  # WHO classification


@dataclass
class OrganicTreatment:
    """Organic/biological intervention details"""
    method_name: str
    materials: List[str]
    preparation_steps: List[str]
    application_method: str
    effectiveness_rating: float  # 0.0 to 1.0
    cost_per_hectare: float
    companion_plants: Optional[List[str]] = None


@dataclass
class ScheduledAction:
    """Individual action in IPM timeline"""
    day: int
    action_type: str
    description: str
    materials_needed: List[str]
    estimated_cost: float


@dataclass
class TreatmentPlan:
    """Complete integrated pest management plan"""
    pest_name: str
    severity: SeverityLevel
    primary_strategy: TreatmentType
    chemical_options: List[ChemicalTreatment]
    organic_options: List[OrganicTreatment]
    cultural_practices: List[str]
    monitoring_schedule: List[str]
    ipm_timeline: List[ScheduledAction]
    total_estimated_cost: float


@dataclass
class EconomicImpact:
    """Financial risk and cost-benefit analysis"""
    potential_yield_loss_pct: float
    estimated_revenue_loss: float
    treatment_cost_range: Dict[str, float]  # {"min": x, "max": y}
    roi_if_treated: float  # Return on investment
    roi_if_untreated: float
    break_even_threshold: float
    recommendation: str  # "Treat immediately", "Monitor", "Economic threshold not met"


@dataclass
class WeatherContext:
    """Environmental conditions affecting pest behavior"""
    temperature: float  # Celsius
    humidity: float  # Percentage
    rainfall_7day: float  # mm
    wind_speed: float  # km/h
    favorable_for_pest: bool
    risk_level: str


@dataclass
class FinalDiagnosticReport:
    """Complete diagnostic output"""
    diagnostic_id: str
    timestamp: datetime
    input_data: DiagnosticInput
    severity_analysis: SeverityAnalysis
    treatment_plan: TreatmentPlan
    economic_impact: EconomicImpact
    weather_context: WeatherContext
    emergency_actions: List[str]
    follow_up_schedule: List[str]
    confidence_notes: str