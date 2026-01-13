"""
Core business logic for The Specialist diagnostic engine.
Pure functions that transform input data into actionable IPM plans.
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import uuid

from models import (
    DiagnosticInput, SeverityAnalysis, SeverityLevel, TreatmentPlan,
    ChemicalTreatment, OrganicTreatment, ScheduledAction, EconomicImpact,
    WeatherContext, FinalDiagnosticReport, TreatmentType, GrowthStage
)
from knowledge_base import (
    SEVERITY_THRESHOLDS, YIELD_LOSS_FACTORS, CHEMICAL_TREATMENTS,
    ORGANIC_TREATMENTS, CULTURAL_PRACTICES, PEST_LIFECYCLES,
    PEST_WEATHER_PREFERENCES
)


def mock_get_weather(location: str) -> Dict[str, float]:
    """
    Mock weather API call. Returns static data for demonstration.
    
    REPLACE THIS: Connect to OpenWeatherMap or similar service.
    
    Args:
        location: Location string (e.g., "Nagpur, India")
    
    Returns:
        Dictionary with weather parameters
    """
    weather_scenarios = {
        "Nagpur": {"temperature": 28.5, "humidity": 75.0, "rainfall_7day": 15.2, "wind_speed": 8.5},
        "Mumbai": {"temperature": 32.0, "humidity": 85.0, "rainfall_7day": 45.0, "wind_speed": 12.0},
        "Default": {"temperature": 25.0, "humidity": 70.0, "rainfall_7day": 10.0, "wind_speed": 5.0}
    }
    
    return weather_scenarios.get(location, weather_scenarios["Default"])


def calculate_severity(
    lesion_pct: float,
    pest_name: str,
    confidence: float,
    growth_stage: GrowthStage
) -> Tuple[SeverityLevel, List[str]]:
    """
    Determine severity level based on affected area and contextual factors.
    
    Args:
        lesion_pct: Percentage of plant/crop affected (0-100)
        pest_name: Name of pest/disease
        confidence: Detection confidence (0.0-1.0)
        growth_stage: Current crop growth stage
    
    Returns:
        Tuple of (SeverityLevel, list of risk factors)
    """
    risk_factors = []
    
    # Get pest-specific thresholds
    thresholds = SEVERITY_THRESHOLDS.get(pest_name, SEVERITY_THRESHOLDS["Fall Armyworm"])
    
    # Adjust for detection confidence
    if confidence < 0.7:
        risk_factors.append("Low detection confidence - verification recommended")
    
    # Adjust for growth stage vulnerability
    critical_stages = [GrowthStage.FLOWERING, GrowthStage.FRUITING]
    if growth_stage in critical_stages:
        risk_factors.append(f"Critical growth stage ({growth_stage.value}) - higher impact expected")
        # Bump severity up one level for critical stages
        lesion_pct = lesion_pct * 1.3
    
    # Determine severity
    if lesion_pct <= thresholds["Low"]["lesion_pct_max"]:
        severity = SeverityLevel.LOW
    elif lesion_pct <= thresholds["Medium"]["lesion_pct_max"]:
        severity = SeverityLevel.MEDIUM
        risk_factors.append("Moderate infestation - immediate action recommended")
    elif lesion_pct <= thresholds["High"]["lesion_pct_max"]:
        severity = SeverityLevel.HIGH
        risk_factors.append("Severe infestation - aggressive treatment required")
    else:
        severity = SeverityLevel.CRITICAL
        risk_factors.append("Critical infestation - crop loss imminent without intervention")
    
    return severity, risk_factors


def estimate_progression_rate(
    pest_name: str,
    weather_data: Dict[str, float],
    severity: SeverityLevel
) -> str:
    """
    Estimate how quickly pest/disease will spread based on conditions.
    
    Args:
        pest_name: Name of pest/disease
        weather_data: Current weather conditions
        severity: Current severity level
    
    Returns:
        "Slow", "Moderate", or "Rapid"
    """
    prefs = PEST_WEATHER_PREFERENCES.get(pest_name, {})
    
    temp = weather_data.get("temperature", 25)
    humidity = weather_data.get("humidity", 70)
    
    optimal_temp = prefs.get("optimal_temp_range", (20, 30))
    optimal_humidity = prefs.get("optimal_humidity_range", (60, 80))
    
    # Check if conditions are optimal
    temp_optimal = optimal_temp[0] <= temp <= optimal_temp[1]
    humidity_optimal = optimal_humidity[0] <= humidity <= optimal_humidity[1]
    
    if temp_optimal and humidity_optimal:
        if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            return "Rapid"
        return "Moderate"
    elif temp_optimal or humidity_optimal:
        return "Moderate"
    else:
        return "Slow"


def estimate_economic_risk(
    severity: SeverityLevel,
    pest_name: str,
    crop_value_per_hectare: float,
    affected_area_pct: float
) -> EconomicImpact:
    """
    Calculate potential financial impact and ROI of treatment.
    
    Args:
        severity: Severity level
        pest_name: Pest/disease name
        crop_value_per_hectare: Expected revenue per hectare (INR)
        affected_area_pct: Percentage of field affected
    
    Returns:
        EconomicImpact dataclass with financial analysis
    """
    # Get yield loss factor
    loss_factors = YIELD_LOSS_FACTORS.get(pest_name, YIELD_LOSS_FACTORS["Fall Armyworm"])
    base_loss_pct = loss_factors.get(severity.value, 0.25)
    
    # Adjust for affected area
    actual_loss_pct = base_loss_pct * (affected_area_pct / 100)
    
    # Calculate revenue loss
    estimated_revenue_loss = crop_value_per_hectare * actual_loss_pct
    
    # Treatment cost estimates (from knowledge base)
    chemical_costs = [c["cost_per_hectare"] for c in CHEMICAL_TREATMENTS.get(pest_name, [])]
    organic_costs = [o["cost_per_hectare"] for o in ORGANIC_TREATMENTS.get(pest_name, [])]
    
    min_treatment_cost = min(chemical_costs + organic_costs) if (chemical_costs or organic_costs) else 500
    max_treatment_cost = max(chemical_costs + organic_costs) if (chemical_costs or organic_costs) else 1500
    
    # Calculate ROI
    avg_treatment_cost = (min_treatment_cost + max_treatment_cost) / 2
    
    # Assume 80% effectiveness of treatment
    potential_savings = estimated_revenue_loss * 0.80
    roi_if_treated = ((potential_savings - avg_treatment_cost) / avg_treatment_cost) * 100
    roi_if_untreated = -100 * actual_loss_pct  # Negative ROI (pure loss)
    
    # Economic threshold
    break_even = avg_treatment_cost / (crop_value_per_hectare * 0.80)
    
    # Recommendation logic
    if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
        recommendation = "Treat immediately - economic threshold exceeded"
    elif estimated_revenue_loss > avg_treatment_cost * 2:
        recommendation = "Treat soon - significant economic benefit expected"
    elif estimated_revenue_loss > avg_treatment_cost:
        recommendation = "Treatment economically justified"
    else:
        recommendation = "Monitor closely - economic threshold not yet met"
    
    return EconomicImpact(
        potential_yield_loss_pct=actual_loss_pct * 100,
        estimated_revenue_loss=estimated_revenue_loss,
        treatment_cost_range={"min": min_treatment_cost, "max": max_treatment_cost},
        roi_if_treated=roi_if_treated,
        roi_if_untreated=roi_if_untreated,
        break_even_threshold=break_even,
        recommendation=recommendation
    )


def get_treatment_plan(
    pest_name: str,
    severity: SeverityLevel,
    location: str
) -> Tuple[List[ChemicalTreatment], List[OrganicTreatment], List[str]]:
    """
    Retrieve and filter appropriate treatments based on severity.
    
    Args:
        pest_name: Pest/disease identifier
        severity: Current severity level
        location: Geographic location (for approval checking)
    
    Returns:
        Tuple of (chemical treatments, organic treatments, cultural practices)
    """
    # Get all treatments for this pest
    all_chemicals = CHEMICAL_TREATMENTS.get(pest_name, [])
    all_organics = ORGANIC_TREATMENTS.get(pest_name, [])
    cultural = CULTURAL_PRACTICES.get(pest_name, [])
    
    # Filter chemicals by severity threshold
    severity_order = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    current_severity_rank = severity_order.get(severity.value, 2)
    
    filtered_chemicals = []
    for chem in all_chemicals:
        chem_threshold = chem.get("severity_threshold", "Medium")
        chem_rank = severity_order.get(chem_threshold, 2)
        
        # Include if chemical's threshold is at or below current severity
        if chem_rank <= current_severity_rank:
            # Check regional approval
            if location in chem.get("approved_regions", []):
                filtered_chemicals.append(ChemicalTreatment(**chem))
    
    # All organic options are always available
    filtered_organics = [OrganicTreatment(**org) for org in all_organics]
    
    return filtered_chemicals, filtered_organics, cultural


def generate_ipm_schedule(
    pest_name: str,
    severity: SeverityLevel,
    treatment_plan: TreatmentPlan,
    use_organic: bool = True
) -> List[ScheduledAction]:
    """
    Create day-by-day IPM implementation timeline.
    
    Args:
        pest_name: Pest/disease name
        severity: Current severity
        treatment_plan: Complete treatment plan
        use_organic: Whether to prioritize organic methods
    
    Returns:
        List of ScheduledAction items
    """
    lifecycle = PEST_LIFECYCLES.get(pest_name, {})
    schedule = []
    
    # Day 0: Immediate actions
    schedule.append(ScheduledAction(
        day=0,
        action_type="Assessment & Preparation",
        description="Conduct field survey, mark affected areas, procure materials",
        materials_needed=["Survey flags", "Notepad", "Camera"],
        estimated_cost=0
    ))
    
    # Day 1: First intervention
    if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
        # Emergency chemical intervention
        if treatment_plan.chemical_options:
            primary_chem = treatment_plan.chemical_options[0]
            schedule.append(ScheduledAction(
                day=1,
                action_type="Chemical Application (Emergency)",
                description=f"Apply {primary_chem.product_name} as emergency measure",
                materials_needed=[primary_chem.product_name, "Sprayer", "PPE", "Water"],
                estimated_cost=primary_chem.cost_per_hectare
            ))
    
    if use_organic and treatment_plan.organic_options:
        primary_organic = treatment_plan.organic_options[0]
        schedule.append(ScheduledAction(
            day=1 if severity in [SeverityLevel.LOW, SeverityLevel.MEDIUM] else 3,
            action_type="Organic Treatment",
            description=f"Apply {primary_organic.method_name}",
            materials_needed=primary_organic.materials,
            estimated_cost=primary_organic.cost_per_hectare
        ))
    
    # Day 3-5: Cultural practices
    schedule.append(ScheduledAction(
        day=3,
        action_type="Cultural Control",
        description="Implement cultural practices: " + ", ".join(treatment_plan.cultural_practices[:2]),
        materials_needed=["Hand tools", "Labor"],
        estimated_cost=200
    ))
    
    # Day 7: Follow-up assessment
    schedule.append(ScheduledAction(
        day=7,
        action_type="Monitoring",
        description="Assess treatment effectiveness, scout for re-infestation",
        materials_needed=["Monitoring forms", "Hand lens"],
        estimated_cost=0
    ))
    
    # Day 10-14: Biological control (if applicable)
    if pest_name in ["Fall Armyworm", "Aphids"]:
        biocontrol = [o for o in treatment_plan.organic_options if "Release" in o.method_name]
        if biocontrol:
            schedule.append(ScheduledAction(
                day=10,
                action_type="Biological Control",
                description=biocontrol[0].method_name,
                materials_needed=biocontrol[0].materials,
                estimated_cost=biocontrol[0].cost_per_hectare
            ))
    
    # Day 14: Second application (if needed)
    if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
        schedule.append(ScheduledAction(
            day=14,
            action_type="Follow-up Treatment",
            description="Second application if pest pressure remains high",
            materials_needed=["Treatment materials (as per day 1)"],
            estimated_cost=treatment_plan.total_estimated_cost * 0.5
        ))
    
    # Day 21: Final assessment
    schedule.append(ScheduledAction(
        day=21,
        action_type="Final Assessment",
        description="Evaluate overall control success, plan preventive measures",
        materials_needed=["Assessment checklist"],
        estimated_cost=0
    ))
    
    return schedule


def analyze_weather_risk(
    pest_name: str,
    weather_data: Dict[str, float]
) -> WeatherContext:
    """
    Evaluate how current weather affects pest behavior.
    
    Args:
        pest_name: Pest/disease name
        weather_data: Current weather conditions
    
    Returns:
        WeatherContext with risk assessment
    """
    prefs = PEST_WEATHER_PREFERENCES.get(pest_name, {})
    
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    rainfall = weather_data.get("rainfall_7day", 0)
    wind = weather_data.get("wind_speed", 0)
    
    optimal_temp = prefs.get("optimal_temp_range", (20, 30))
    optimal_humidity = prefs.get("optimal_humidity_range", (60, 80))
    
    # Check favorability
    temp_favorable = optimal_temp[0] <= temp <= optimal_temp[1]
    humidity_favorable = optimal_humidity[0] <= humidity <= optimal_humidity[1]
    
    favorable_for_pest = temp_favorable and humidity_favorable
    
    # Risk level
    if favorable_for_pest:
        if rainfall > 20 and prefs.get("rainfall_preference") == "high":
            risk_level = "Very High"
        else:
            risk_level = "High"
    elif temp_favorable or humidity_favorable:
        risk_level = "Moderate"
    else:
        risk_level = "Low"
    
    return WeatherContext(
        temperature=temp,
        humidity=humidity,
        rainfall_7day=rainfall,
        wind_speed=wind,
        favorable_for_pest=favorable_for_pest,
        risk_level=risk_level
    )


def generate_diagnostic_report(diagnostic_input: DiagnosticInput) -> FinalDiagnosticReport:
    """
    Main orchestration function that generates complete diagnostic report.
    
    Args:
        diagnostic_input: Input data from detection system
    
    Returns:
        Complete diagnostic report with all analyses
    """
    # Step 1: Get weather context
    weather_data = mock_get_weather(diagnostic_input.location)
    weather_context = analyze_weather_risk(diagnostic_input.pest_name, weather_data)
    
    # Step 2: Calculate severity
    severity, risk_factors = calculate_severity(
        diagnostic_input.lesion_percentage,
        diagnostic_input.pest_name,
        diagnostic_input.confidence,
        diagnostic_input.growth_stage
    )
    
    # Step 3: Estimate progression
    progression = estimate_progression_rate(
        diagnostic_input.pest_name,
        weather_data,
        severity
    )
    
    # Build severity analysis
    severity_analysis = SeverityAnalysis(
        severity_level=severity,
        affected_area_pct=diagnostic_input.lesion_percentage,
        confidence_score=diagnostic_input.confidence,
        risk_factors=risk_factors,
        progression_rate=progression,
        reasoning=f"Based on {diagnostic_input.lesion_percentage}% affected area at {diagnostic_input.growth_stage.value} stage, "
                  f"classified as {severity.value}. Weather conditions are {weather_context.risk_level} risk for {diagnostic_input.pest_name}."
    )
    
    # Step 4: Get treatment options
    chemicals, organics, cultural = get_treatment_plan(
        diagnostic_input.pest_name,
        severity,
        diagnostic_input.location
    )
    
    # Step 5: Calculate costs
    total_cost = 0
    if chemicals:
        total_cost = min([c.cost_per_hectare for c in chemicals])
    elif organics:
        total_cost = min([o.cost_per_hectare for o in organics])
    
    # Step 6: Build treatment plan
    treatment_plan = TreatmentPlan(
        pest_name=diagnostic_input.pest_name,
        severity=severity,
        primary_strategy=TreatmentType.ORGANIC if severity == SeverityLevel.LOW else TreatmentType.CHEMICAL,
        chemical_options=chemicals,
        organic_options=organics,
        cultural_practices=cultural,
        monitoring_schedule=[
            "Daily scouting for 7 days",
            "Weekly monitoring for 3 weeks",
            "Record pest counts and damage levels"
        ],
        ipm_timeline=[],  # Will be populated next
        total_estimated_cost=total_cost
    )
    
    # Step 7: Generate IPM schedule
    treatment_plan.ipm_timeline = generate_ipm_schedule(
        diagnostic_input.pest_name,
        severity,
        treatment_plan,
        use_organic=(severity in [SeverityLevel.LOW, SeverityLevel.MEDIUM])
    )
    
    # Step 8: Economic analysis
    economic_impact = estimate_economic_risk(
        severity,
        diagnostic_input.pest_name,
        diagnostic_input.crop_value_per_hectare,
        diagnostic_input.lesion_percentage
    )
    
    # Step 9: Emergency actions
    emergency_actions = []
    if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
        emergency_actions = [
            f"Immediately isolate affected area to prevent spread",
            f"Begin treatment within 24 hours",
            f"Notify neighboring farmers if {diagnostic_input.pest_name} is quarantine pest",
            "Document damage with photos for insurance purposes"
        ]
    
    # Step 10: Follow-up schedule
    follow_up = [
        "Day 3: Check treatment efficacy",
        "Day 7: First detailed assessment",
        "Day 14: Second treatment if needed",
        "Day 21: Final evaluation and preventive planning"
    ]
    
    # Step 11: Confidence notes
    confidence_notes = f"Detection confidence: {diagnostic_input.confidence*100:.1f}%. "
    if diagnostic_input.confidence < 0.75:
        confidence_notes += "Recommend laboratory confirmation for definitive diagnosis."
    else:
        confidence_notes += "High confidence - proceed with recommended treatments."
    
    # Generate unique ID
    diagnostic_id = f"DIAG-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    
    return FinalDiagnosticReport(
        diagnostic_id=diagnostic_id,
        timestamp=datetime.now(),
        input_data=diagnostic_input,
        severity_analysis=severity_analysis,
        treatment_plan=treatment_plan,
        economic_impact=economic_impact,
        weather_context=weather_context,
        emergency_actions=emergency_actions,
        follow_up_schedule=follow_up,
        confidence_notes=confidence_notes
    )