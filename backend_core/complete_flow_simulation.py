"""
COMPLETE END-TO-END SIMULATION
Demonstrates the full flow from image upload to IPM plan generation.

Flow:
1. Farmer uploads image
2. Gemini Vision analyzes image
3. Our diagnostic system processes results
4. IPM plan generated with lifecycle insights and dual treatments
"""

import json
from datetime import datetime
from typing import Dict

# Our existing modules
from models import DiagnosticInput, GrowthStage
from logic import generate_diagnostic_report, mock_get_weather

# NEW: Gemini integration (mock version for demo)
class MockGeminiVisionAnalyzer:
    """
    Mock version of Gemini Vision analyzer for demonstration.
    Replace this with real gemini_vision.py in production.
    """
    
    def analyze_image(self, image_path: str, crop_type: str, location: str) -> Dict:
        """
        Simulates what Gemini Vision would return.
        
        In production, this would:
        1. Send image to Gemini API
        2. Get structured JSON response
        3. Parse pest identification
        """
        
        # Simulate different scenarios based on image filename
        scenarios = {
            "armyworm": {
                "pest_name": "Fall Armyworm",
                "confidence": 0.94,
                "lesion_percentage": 22.5,
                "visual_symptoms": [
                    "Irregular holes in leaves",
                    "Frass (insect droppings) visible on leaves",
                    "Entry holes in whorl",
                    "Larvae visible in leaf folds"
                ],
                "lifecycle_stage": "Late Larva (L4-L5)",
                "urgency_level": "High",
                "reasoning": "Multiple feeding holes and presence of frass indicate active larval feeding. Late instar larvae (L4-L5) are most destructive. High humidity conditions favor continued development."
            },
            "blight": {
                "pest_name": "Late Blight",
                "confidence": 0.89,
                "lesion_percentage": 35.8,
                "visual_symptoms": [
                    "Water-soaked lesions on lower leaves",
                    "Brown spots with yellow halos",
                    "White fungal growth on leaf undersides",
                    "Rapid spread pattern visible"
                ],
                "lifecycle_stage": "Sporulation Phase",
                "urgency_level": "Critical",
                "reasoning": "Lesions showing sporulation (white growth) indicate active disease spread. Current weather (high humidity, moderate temperature) is ideal for pathogen. Disease progresses rapidly in these conditions - immediate intervention required."
            },
            "aphids": {
                "pest_name": "Aphids",
                "confidence": 0.96,
                "lesion_percentage": 18.3,
                "visual_symptoms": [
                    "Curled and distorted young leaves",
                    "Honeydew (sticky substance) on leaves",
                    "Sooty mold growing on honeydew",
                    "Green aphids clustered on shoot tips",
                    "Presence of winged aphids (indicates colony maturity)"
                ],
                "lifecycle_stage": "Adult Colony (Reproducing)",
                "urgency_level": "Medium",
                "reasoning": "Established colony with winged adults present indicates population ready to migrate. Curling leaves show sustained feeding. However, damage is still manageable with proper intervention."
            }
        }
        
        # Determine scenario from image path
        if "armyworm" in image_path.lower():
            return scenarios["armyworm"]
        elif "blight" in image_path.lower():
            return scenarios["blight"]
        elif "aphid" in image_path.lower():
            return scenarios["aphids"]
        else:
            # Default scenario
            return scenarios["armyworm"]


def print_section(title: str, emoji: str = "📋"):
    """Pretty print section headers"""
    print(f"\n{emoji} " + "="*70)
    print(f"{emoji} {title}")
    print(f"{emoji} " + "="*70)


def simulate_farmer_workflow(
    farmer_name: str,
    image_path: str,
    crop_type: str,
    crop_value: float,
    location: str,
    growth_stage: str
):
    """
    Simulate complete workflow from a farmer's perspective.
    
    This is what happens when a farmer:
    1. Takes a photo
    2. Uploads to The Specialist
    3. Receives IPM recommendations
    """
    
    print_section(f"FARMER: {farmer_name}", "👨‍🌾")
    print(f"Location: {location}")
    print(f"Crop: {crop_type} ({growth_stage} stage)")
    print(f"Crop Value: ₹{crop_value:,.2f}/hectare")
    print(f"Image: {image_path}")
    
    # ========================================================================
    # STEP 1: GEMINI VISION ANALYSIS
    # ========================================================================
    print_section("STEP 1: AI Image Analysis (Gemini Vision)", "🤖")
    print("Processing uploaded image...")
    
    gemini = MockGeminiVisionAnalyzer()
    detection = gemini.analyze_image(
        image_path=image_path,
        crop_type=crop_type,
        location=location
    )
    
    print(f"\n✅ Detection Complete!")
    print(f"\n   🐛 PEST IDENTIFIED: {detection['pest_name']}")
    print(f"   📊 Confidence: {detection['confidence']*100:.1f}%")
    print(f"   📏 Affected Area: {detection['lesion_percentage']:.1f}%")
    print(f"   🔬 Lifecycle Stage: {detection['lifecycle_stage']}")
    print(f"   ⚠️  Urgency: {detection['urgency_level']}")
    
    print(f"\n   🔍 Visual Symptoms Detected:")
    for symptom in detection['visual_symptoms']:
        print(f"      • {symptom}")
    
    print(f"\n   💭 AI Reasoning:")
    print(f"      {detection['reasoning']}")
    
    # ========================================================================
    # STEP 2: LIFECYCLE INSIGHTS (THE STRATEGIST)
    # ========================================================================
    print_section("STEP 2: Lifecycle Analysis & Threat Assessment", "🔬")
    
    # Get weather context
    weather = mock_get_weather(location)
    
    print(f"Current Environmental Conditions:")
    print(f"   🌡️  Temperature: {weather['temperature']}°C")
    print(f"   💧 Humidity: {weather['humidity']}%")
    print(f"   🌧️  Rainfall (7-day): {weather['rainfall_7day']}mm")
    
    print(f"\n📚 Lifecycle Stage: {detection['lifecycle_stage']}")
    print(f"   ⏰ Why timing matters:")
    
    if "Larva" in detection['lifecycle_stage']:
        print(f"      • Larvae are ACTIVELY FEEDING - damage will increase rapidly")
        print(f"      • Current stage is vulnerable to Bt and other bio-pesticides")
        print(f"      • Will pupate in ~7-10 days, after which treatment is ineffective")
        print(f"      • Optimal treatment window: NEXT 3-5 DAYS")
    elif "Sporulation" in detection['lifecycle_stage']:
        print(f"      • Disease is actively producing spores - spreads exponentially")
        print(f"      • Each lesion releases millions of spores in humid conditions")
        print(f"      • Wind and rain will spread to neighboring plants/fields")
        print(f"      • Optimal treatment window: IMMEDIATE (within 24 hours)")
    elif "Adult Colony" in detection['lifecycle_stage']:
        print(f"      • Adults reproduce rapidly - population doubles every 7-10 days")
        print(f"      • Winged forms will migrate to new plants")
        print(f"      • Honeydew attracts ants and promotes sooty mold")
        print(f"      • Optimal treatment window: NEXT 1-2 DAYS before migration")
    
    # ========================================================================
    # STEP 3: GENERATE DIAGNOSTIC REPORT (OUR CORE SYSTEM)
    # ========================================================================
    print_section("STEP 3: Generating IPM Strategy", "🎯")
    
    diagnostic_input = DiagnosticInput(
        pest_name=detection['pest_name'],
        confidence=detection['confidence'],
        lesion_percentage=detection['lesion_percentage'],
        growth_stage=GrowthStage(growth_stage),
        crop_type=crop_type,
        crop_value_per_hectare=crop_value,
        location=location,
        visual_symptoms=detection['visual_symptoms']
    )
    
    print("Analyzing economic impact...")
    print("Selecting optimal treatments...")
    print("Generating IPM timeline...")
    
    report = generate_diagnostic_report(diagnostic_input)
    
    # ========================================================================
    # STEP 4: DUAL TREATMENT RECOMMENDATIONS
    # ========================================================================
    print_section("STEP 4: Treatment Options (Organic + Chemical)", "💊")
    
    print(f"Severity Level: {report.severity_analysis.severity_level.value}")
    print(f"Primary Strategy: {report.treatment_plan.primary_strategy.value}")
    
    # ORGANIC OPTIONS
    print(f"\n🌿 ORGANIC TREATMENTS (Sustainable Options):")
    for i, organic in enumerate(report.treatment_plan.organic_options[:2], 1):
        print(f"\n   Option {i}: {organic.method_name}")
        print(f"   ✓ Effectiveness: {organic.effectiveness_rating*100:.0f}%")
        print(f"   ✓ Cost: ₹{organic.cost_per_hectare:,.2f}/hectare")
        print(f"   ✓ Materials: {', '.join(organic.materials[:3])}")
        print(f"   ✓ Application: {organic.application_method}")
        if organic.companion_plants:
            print(f"   ✓ Companion Plants: {', '.join(organic.companion_plants)}")
    
    # CHEMICAL OPTIONS
    print(f"\n⚗️  CHEMICAL TREATMENTS (If Organic Insufficient):")
    for i, chemical in enumerate(report.treatment_plan.chemical_options[:2], 1):
        print(f"\n   Option {i}: {chemical.product_name}")
        print(f"   ✓ Active Ingredient: {chemical.active_ingredient}")
        print(f"   ✓ Dosage: {chemical.dosage}")
        print(f"   ✓ Cost: ₹{chemical.cost_per_hectare:,.2f}/hectare")
        print(f"   ⚠️  Safety:")
        print(f"      • Re-Entry Interval: {chemical.rei_hours} hours")
        print(f"      • Pre-Harvest Interval: {chemical.phi_days} days")
        print(f"      • PPE Required: {', '.join(chemical.ppe_required)}")
        print(f"      • Toxicity Class: {chemical.toxicity_class}")
    
    # ========================================================================
    # STEP 5: IPM STRATEGY (THE STRATEGIST)
    # ========================================================================
    print_section("STEP 5: Integrated Pest Management Plan", "📅")
    
    print("🎯 COMPANION PLANTING RECOMMENDATIONS:")
    for i, practice in enumerate(report.treatment_plan.cultural_practices[:3], 1):
        print(f"   {i}. {practice}")
    
    print(f"\n🌦️  PREDICTIVE RISK ASSESSMENT:")
    print(f"   Weather Favorability: {report.weather_context.risk_level}")
    if report.weather_context.favorable_for_pest:
        print(f"   ⚠️  Current conditions FAVOR pest development")
        print(f"   → Monitor closely, pest population may increase rapidly")
    else:
        print(f"   ✓ Current conditions NOT optimal for pest")
        print(f"   → Conditions may slow pest development")
    
    print(f"\n⏰ TIMING OPTIMIZATION (IPM Schedule):")
    print(f"   Recommended application timing based on:")
    print(f"   • Pest lifecycle stage: {detection['lifecycle_stage']}")
    print(f"   • Weather conditions: {weather['wind_speed']} km/h wind")
    print(f"   • Crop vulnerability: {growth_stage} stage")
    
    print(f"\n   📋 ACTION TIMELINE:")
    for action in report.treatment_plan.ipm_timeline[:5]:
        cost_str = f"(₹{action.estimated_cost:,.0f})" if action.estimated_cost > 0 else ""
        print(f"   Day {action.day:2d}: {action.action_type} {cost_str}")
        print(f"           → {action.description}")
    
    # ========================================================================
    # STEP 6: ECONOMIC JUSTIFICATION
    # ========================================================================
    print_section("STEP 6: Economic Analysis", "💰")
    
    print(f"Potential Yield Loss: {report.economic_impact.potential_yield_loss_pct:.1f}%")
    print(f"Estimated Revenue Loss: ₹{report.economic_impact.estimated_revenue_loss:,.2f}")
    print(f"\nTreatment Investment:")
    print(f"   Min Cost: ₹{report.economic_impact.treatment_cost_range['min']:,.2f}")
    print(f"   Max Cost: ₹{report.economic_impact.treatment_cost_range['max']:,.2f}")
    print(f"\nReturn on Investment:")
    print(f"   If Treated: {report.economic_impact.roi_if_treated:,.1f}%")
    print(f"   If Untreated: {report.economic_impact.roi_if_untreated:,.1f}%")
    print(f"\n💡 Recommendation: {report.economic_impact.recommendation}")
    
    # ========================================================================
    # STEP 7: EMERGENCY ACTIONS (IF CRITICAL)
    # ========================================================================
    if report.emergency_actions:
        print_section("STEP 7: ⚠️  EMERGENCY ACTIONS REQUIRED", "🚨")
        for i, action in enumerate(report.emergency_actions, 1):
            print(f"   {i}. {action}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_section("SUMMARY FOR FARMER", "✅")
    print(f"Diagnostic ID: {report.diagnostic_id}")
    print(f"Confidence: {report.confidence_notes}")
    print(f"\n🎯 KEY TAKEAWAYS:")
    print(f"   1. Pest: {detection['pest_name']} at {detection['lifecycle_stage']}")
    print(f"   2. Urgency: {detection['urgency_level']} - {report.economic_impact.recommendation}")
    print(f"   3. Best Treatment: {report.treatment_plan.organic_options[0].method_name if report.treatment_plan.organic_options else 'See recommendations'}")
    print(f"   4. Expected Cost: ₹{report.treatment_plan.total_estimated_cost:,.2f}")
    print(f"   5. Potential Savings: ₹{report.economic_impact.estimated_revenue_loss - report.treatment_plan.total_estimated_cost:,.2f}")
    
    print("\n" + "="*80 + "\n")
    
    return report


def main():
    """Run complete flow simulations"""
    
    print("\n" + "🌾"*40)
    print(" "*25 + "THE SPECIALIST")
    print(" "*15 + "Complete AI-Powered Agricultural Diagnostic System")
    print(" "*20 + "Image → Gemini → IPM Strategy")
    print("🌾"*40 + "\n")
    
    # Scenario 1: Fall Armyworm
    print("\n" + "▓"*80)
    print("SCENARIO 1: FALL ARMYWORM OUTBREAK")
    print("▓"*80)
    
    report1 = simulate_farmer_workflow(
        farmer_name="Rajesh Kumar",
        image_path="uploads/fall_armyworm_maize.jpg",
        crop_type="Maize",
        crop_value=85000.0,
        location="Nagpur",
        growth_stage="Vegetative"
    )
    
    input("\n[Press Enter to see next scenario...]\n")
    
    # Scenario 2: Late Blight
    print("\n" + "▓"*80)
    print("SCENARIO 2: LATE BLIGHT CRISIS")
    print("▓"*80)
    
    report2 = simulate_farmer_workflow(
        farmer_name="Priya Sharma",
        image_path="uploads/late_blight_potato.jpg",
        crop_type="Potato",
        crop_value=150000.0,
        location="Mumbai",
        growth_stage="Flowering"
    )
    
    input("\n[Press Enter to see next scenario...]\n")
    
    # Scenario 3: Aphids
    print("\n" + "▓"*80)
    print("SCENARIO 3: APHID INFESTATION")
    print("▓"*80)
    
    report3 = simulate_farmer_workflow(
        farmer_name="Mohammed Ali",
        image_path="uploads/aphid_cotton.jpg",
        crop_type="Cotton",
        crop_value=120000.0,
        location="Nagpur",
        growth_stage="Fruiting"
    )
    
    # Final Summary
    print_section("🎯 SYSTEM CAPABILITIES DEMONSTRATED", "✨")
    print("\n✅ Gemini Vision Integration:")
    print("   • Accurate pest identification from images")
    print("   • Confidence scoring for reliability")
    print("   • Lifecycle stage detection for timing")
    print("   • Visual symptom analysis")
    
    print("\n✅ Lifecycle Insights (The Strategist):")
    print("   • Explains urgency based on pest development stage")
    print("   • Optimal treatment windows identified")
    print("   • Weather correlation for risk prediction")
    
    print("\n✅ Dual Treatment Approach:")
    print("   • Organic methods prioritized (sustainability)")
    print("   • Chemical options with full safety protocols")
    print("   • Cost comparison for informed decisions")
    
    print("\n✅ IPM Strategy:")
    print("   • Companion planting suggestions")
    print("   • Timing optimization (weather + lifecycle)")
    print("   • Cultural practices integration")
    print("   • Day-by-day action plan")
    
    print("\n✅ Economic Intelligence:")
    print("   • ROI calculations")
    print("   • Yield loss predictions")
    print("   • Break-even analysis")
    
    print("\n" + "="*80)
    print("🌟 THE SPECIALIST: From Image to Action in Seconds")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()