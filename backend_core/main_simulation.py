"""
Simulation script to demonstrate The Specialist diagnostic engine.
Runs realistic test cases and outputs formatted reports.
"""

import json
from datetime import datetime
from models import DiagnosticInput, GrowthStage
from logic import generate_diagnostic_report


def format_report_as_json(report) -> str:
    """
    Convert diagnostic report to JSON format.
    Handles dataclass serialization with recursion protection.
    """
    def serialize(obj, seen=None):
        if seen is None:
            seen = set()
        
        # Prevent circular references
        obj_id = id(obj)
        if obj_id in seen:
            return f"<circular reference to {type(obj).__name__}>"
        
        # Handle datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # Handle Enums
        if hasattr(obj, 'value') and hasattr(obj, 'name'):
            return obj.value
        
        # Handle lists
        if isinstance(obj, list):
            return [serialize(item, seen) for item in obj]
        
        # Handle dicts
        if isinstance(obj, dict):
            return {k: serialize(v, seen) for k, v in obj.items()}
        
        # Handle dataclasses and objects with __dict__
        if hasattr(obj, '__dict__'):
            seen.add(obj_id)
            try:
                result = {k: serialize(v, seen.copy()) for k, v in obj.__dict__.items()}
                return result
            except:
                return str(obj)
        
        # Handle primitive types
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        
        # Fallback
        return str(obj)
    
    return json.dumps(serialize(report), indent=2, ensure_ascii=False)


def print_section_header(title: str):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def run_simulation(scenario_name: str, diagnostic_input: DiagnosticInput):
    """
    Run a single diagnostic simulation and print results.
    
    Args:
        scenario_name: Name of test scenario
        diagnostic_input: Input data for diagnosis
    """
    print_section_header(f"SCENARIO: {scenario_name}")
    
    print(f"\n📊 INPUT DATA:")
    print(f"  Pest Detected: {diagnostic_input.pest_name}")
    print(f"  Confidence: {diagnostic_input.confidence*100:.1f}%")
    print(f"  Affected Area: {diagnostic_input.lesion_percentage:.1f}%")
    print(f"  Growth Stage: {diagnostic_input.growth_stage.value}")
    print(f"  Crop: {diagnostic_input.crop_type}")
    print(f"  Location: {diagnostic_input.location}")
    print(f"  Crop Value: ₹{diagnostic_input.crop_value_per_hectare:,.2f}/hectare")
    
    # Generate report
    report = generate_diagnostic_report(diagnostic_input)
    
    # Display key results
    print(f"\n🔍 SEVERITY ANALYSIS:")
    print(f"  Level: {report.severity_analysis.severity_level.value}")
    print(f"  Progression Rate: {report.severity_analysis.progression_rate}")
    print(f"  Risk Factors:")
    for factor in report.severity_analysis.risk_factors:
        print(f"    • {factor}")
    
    print(f"\n💰 ECONOMIC IMPACT:")
    print(f"  Potential Yield Loss: {report.economic_impact.potential_yield_loss_pct:.1f}%")
    print(f"  Estimated Revenue Loss: ₹{report.economic_impact.estimated_revenue_loss:,.2f}")
    print(f"  Treatment Cost Range: ₹{report.economic_impact.treatment_cost_range['min']:,.2f} - ₹{report.economic_impact.treatment_cost_range['max']:,.2f}")
    print(f"  ROI if Treated: {report.economic_impact.roi_if_treated:.1f}%")
    print(f"  Recommendation: {report.economic_impact.recommendation}")
    
    print(f"\n🌦️  WEATHER CONTEXT:")
    print(f"  Temperature: {report.weather_context.temperature}°C")
    print(f"  Humidity: {report.weather_context.humidity}%")
    print(f"  Risk Level: {report.weather_context.risk_level}")
    print(f"  Favorable for Pest: {'Yes' if report.weather_context.favorable_for_pest else 'No'}")
    
    print(f"\n💊 TREATMENT OPTIONS:")
    print(f"  Primary Strategy: {report.treatment_plan.primary_strategy.value}")
    print(f"\n  Chemical Options ({len(report.treatment_plan.chemical_options)}):")
    for i, chem in enumerate(report.treatment_plan.chemical_options[:2], 1):
        print(f"    {i}. {chem.product_name}")
        print(f"       Dosage: {chem.dosage}")
        print(f"       Cost: ₹{chem.cost_per_hectare:,.2f}/ha")
        print(f"       PHI: {chem.phi_days} days")
    
    print(f"\n  Organic Options ({len(report.treatment_plan.organic_options)}):")
    for i, org in enumerate(report.treatment_plan.organic_options[:2], 1):
        print(f"    {i}. {org.method_name}")
        print(f"       Effectiveness: {org.effectiveness_rating*100:.0f}%")
        print(f"       Cost: ₹{org.cost_per_hectare:,.2f}/ha")
    
    print(f"\n📅 IPM SCHEDULE (First 7 days):")
    for action in report.treatment_plan.ipm_timeline[:4]:
        print(f"  Day {action.day}: {action.action_type}")
        print(f"    → {action.description}")
        if action.estimated_cost > 0:
            print(f"    💵 ₹{action.estimated_cost:,.2f}")
    
    if report.emergency_actions:
        print(f"\n⚠️  EMERGENCY ACTIONS:")
        for action in report.emergency_actions:
            print(f"  • {action}")
    
    print(f"\n📋 CULTURAL PRACTICES:")
    for practice in report.treatment_plan.cultural_practices[:3]:
        print(f"  • {practice}")
    
    print(f"\n✅ CONFIDENCE ASSESSMENT:")
    print(f"  {report.confidence_notes}")
    
    # Export full JSON
    print(f"\n📄 FULL JSON REPORT:")
    print("-" * 80)
    json_report = format_report_as_json(report)
    # Print first 50 lines of JSON
    json_lines = json_report.split('\n')
    for line in json_lines[:50]:
        print(line)
    if len(json_lines) > 50:
        print(f"... ({len(json_lines) - 50} more lines)")
    
    print("\n" + "="*80 + "\n")
    
    return report


def main():
    """
    Run multiple diagnostic scenarios to demonstrate system capabilities.
    """
    print("\n" + "🌾"*40)
    print(" "*20 + "THE SPECIALIST")
    print(" "*10 + "Agricultural Diagnostic Engine - Core Simulation")
    print("🌾"*40)
    
    # Scenario 1: Early Fall Armyworm infestation
    scenario1 = DiagnosticInput(
        pest_name="Fall Armyworm",
        confidence=0.92,
        lesion_percentage=15.5,
        growth_stage=GrowthStage.VEGETATIVE,
        crop_type="Maize",
        crop_value_per_hectare=85000.0,
        location="Nagpur",
        visual_symptoms=["Leaf damage", "Frass on leaves", "Entry holes"]
    )
    
    report1 = run_simulation("Early Fall Armyworm Detection", scenario1)
    
    # Scenario 2: Critical Late Blight outbreak
    scenario2 = DiagnosticInput(
        pest_name="Late Blight",
        confidence=0.88,
        lesion_percentage=45.0,
        growth_stage=GrowthStage.FLOWERING,
        crop_type="Potato",
        crop_value_per_hectare=150000.0,
        location="Mumbai",
        visual_symptoms=["Water-soaked lesions", "White fungal growth", "Stem infection"]
    )
    
    report2 = run_simulation("Critical Late Blight Outbreak", scenario2)
    
    # Scenario 3: Moderate Aphid infestation
    scenario3 = DiagnosticInput(
        pest_name="Aphids",
        confidence=0.95,
        lesion_percentage=28.0,
        growth_stage=GrowthStage.FRUITING,
        crop_type="Cotton",
        crop_value_per_hectare=120000.0,
        location="Nagpur",
        visual_symptoms=["Curled leaves", "Honeydew presence", "Sooty mold"]
    )
    
    report3 = run_simulation("Moderate Aphid Infestation", scenario3)
    
    print_section_header("SIMULATION COMPLETE")
    print("\n✅ All diagnostic scenarios processed successfully!")
    print("\n📊 Summary:")
    print(f"  • Scenario 1 Severity: {report1.severity_analysis.severity_level.value}")
    print(f"  • Scenario 2 Severity: {report2.severity_analysis.severity_level.value}")
    print(f"  • Scenario 3 Severity: {report3.severity_analysis.severity_level.value}")
    print("\n💡 Next Steps:")
    print("  1. Review ARCHITECTURE_GUIDE.md to understand data flow")
    print("  2. Check TODO_NEXT.md for production integration tasks")
    print("  3. Replace mock functions with real API connections")
    print("  4. Integrate with FastAPI endpoints when ready")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()