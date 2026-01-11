"""
Integration Demo - Agricultural Diagnostic Engine

Demonstrates the complete workflow:
1. ChemicalDatabase lookups
2. ScoringEngine recalculation
3. Pydantic model validation
4. Complete diagnostic flow

Run: python -m app.tests.integration_demo
"""

from datetime import datetime
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
)


def example_complete_workflow():
    """Complete diagnosis workflow."""
    print("=" * 80)
    print("COMPLETE DIAGNOSIS WORKFLOW")
    print("=" * 80)
    
    chemical_db = ChemicalDatabase()
    scoring_engine = ScoringEngine()
    
    # Step 1: VLM Analysis Result
    print("\n[STEP 1] Vision Language Model Analysis")
    vlm_result = {
        "crop": "tomato",
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
    
    print(f"Pest: {vlm_result['identified_pest']}")
    print(f"Raw Confidence: {vlm_result['raw_confidence']:.1%}")
    print(f"Growth Stage: {vlm_result['growth_stage']}")
    
    # Step 2: Apply ScoringEngine
    print("\n[STEP 2] ScoringEngine Recalculation")
    evidence_found = vlm_result['visible_symptoms']
    required_evidence = ["necrotic lesion", "characteristic rings", "discoloration"]
    
    recalculated_confidence = scoring_engine.calculate_confidence(
        raw_prob=vlm_result['raw_confidence'],
        evidence_found=evidence_found,
        required_evidence=required_evidence
    )
    
    recalculated_severity = scoring_engine.calculate_severity(
        lesion_area_pct=vlm_result['lesion_coverage_percent'],
        growth_stage=vlm_result['growth_stage']
    )
    
    print(f"Confidence: {vlm_result['raw_confidence']:.3f} → {recalculated_confidence:.3f}")
    print(f"Severity: {recalculated_severity}")
    
    # Step 3: Lookup ChemicalDatabase
    print("\n[STEP 3] Chemical Database Lookup")
    pest_name = vlm_result['identified_pest']
    treatments = chemical_db.get_safe_treatment(
        pest_name,
        Region.NORTH_AMERICA,
        "tomato"
    )
    
    print(f"Treatments found: {len(treatments)}")
    for treatment in treatments:
        print(f"  - {treatment['product_name']} ({treatment['effectiveness_rate']:.0%} effective)")
    
    # Step 4: Create DiagnosticResult
    print("\n[STEP 4] Create DiagnosticResult")
    
    evidence_list = [
        VisualEvidence(
            description="Concentric rings with yellow halo on tomato leaves",
            confidence=0.92,
            location="Lower leaf surface"
        ),
        VisualEvidence(
            description="Brown necrotic lesions characteristic of Early Blight",
            confidence=0.88,
            location="Leaf center"
        ),
    ]
    
    diagnosis = Diagnosis(
        label=pest_name,
        confidence=recalculated_confidence,
        visual_evidence=evidence_list
    )
    
    organic_treatments = [
        OrganicTreatment(
            treatment_name="Neem Oil",
            dosage="2-3%",
            application_frequency="Every 7 days",
            description="Natural oil that disrupts insect growth",
            effectiveness_rate=0.68
        ),
    ]
    
    chemical_treatments = []
    for db_treatment in treatments:
        chem = ChemicalTreatment(
            treatment_name=db_treatment['product_name'],
            active_ingredient=db_treatment['active_ingredient'],
            dosage=db_treatment['dosage'],
            application_frequency=db_treatment['application_frequency'],
            description=f"Pre-harvest interval: {db_treatment['pre_harvest_interval']} days",
            effectiveness_rate=db_treatment['effectiveness_rate'],
            safety_equipment=["Gloves", "Respirator"],
            re_entry_interval=db_treatment['re_entry_interval'],
        )
        chemical_treatments.append(chem)
    
    treatment_plan = TreatmentPlan(
        organic_treatments=organic_treatments,
        chemical_treatments=chemical_treatments,
    )
    
    severity_analysis = SeverityAnalysis(
        severity_index=SeverityLevel.MEDIUM,
        quantitative_score=0.45,
        stage=CropStage.VEGETATIVE,
        affected_area_percentage=18.5
    )
    
    economic_impact = EconomicImpact(
        yield_loss_estimate="8.5%",
        urgency_level=UrgencyLevel.MEDIUM
    )
    
    diagnostic_result = DiagnosticResult(
        diagnosis=diagnosis,
        severity_analysis=severity_analysis,
        economic_impact=economic_impact,
        treatment_plan=treatment_plan,
        confidence_overall=recalculated_confidence
    )
    
    print("✓ DiagnosticResult created successfully")
    print(f"  Confidence: {diagnostic_result.confidence_overall:.3f}")
    print(f"  Severity: {diagnostic_result.severity_analysis.severity_index}")
    print(f"  Treatments: {len(treatment_plan.chemical_treatments)} chemical, {len(treatment_plan.organic_treatments)} organic")
    
    return diagnostic_result


def example_confidence_scenarios():
    """Demonstrate confidence adjustments."""
    print("\n" + "=" * 80)
    print("CONFIDENCE ADJUSTMENT SCENARIOS")
    print("=" * 80)
    
    engine = ScoringEngine()
    
    scenarios = [
        ("Strong Evidence", 0.90, ["ring", "halo", "lesion"], ["ring", "halo", "lesion"]),
        ("Weak Evidence", 0.90, ["ring"], ["ring", "halo", "lesion"]),
        ("Low Raw + Strong Evidence", 0.50, ["ring", "halo", "lesion"], ["ring", "halo", "lesion"]),
    ]
    
    for name, raw_prob, found, required in scenarios:
        adjusted = engine.calculate_confidence(raw_prob, found, required)
        print(f"{name}: {raw_prob:.2f} → {adjusted:.2f}")


def example_severity_scenarios():
    """Demonstrate severity classification."""
    print("\n" + "=" * 80)
    print("SEVERITY BY GROWTH STAGE")
    print("=" * 80)
    
    engine = ScoringEngine()
    
    scenarios = [
        ("Seedling", 8.0),
        ("Vegetative", 18.5),
        ("Flowering", 25.0),
        ("Mature", 40.0),
    ]
    
    for stage, lesion_pct in scenarios:
        severity = engine.calculate_severity(lesion_pct, stage)
        print(f"{stage:15} {lesion_pct:5.1f}% → {severity}")


if __name__ == "__main__":
    example_complete_workflow()
    example_confidence_scenarios()
    example_severity_scenarios()
    
    print("\n" + "=" * 80)
    print("✓ All integration examples completed")
    print("=" * 80)
