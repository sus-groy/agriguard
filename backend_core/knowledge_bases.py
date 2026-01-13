"""
Static knowledge base for pest/disease management.
Acts as mock database until replaced with PostgreSQL/MongoDB.
"""

# Pest lifecycle data (days for each stage)
PEST_LIFECYCLES = {
    "Fall Armyworm": {
        "egg": 3,
        "larva": 14,
        "pupa": 10,
        "adult": 10,
        "total_cycle": 37,
        "vulnerable_stages": ["egg", "early_larva"],
        "peak_damage_stage": "larva"
    },
    "Late Blight": {
        "spore_germination": 2,
        "infection": 5,
        "sporulation": 7,
        "spread": 3,
        "total_cycle": 17,
        "vulnerable_stages": ["spore_germination"],
        "peak_damage_stage": "sporulation"
    },
    "Aphids": {
        "nymph": 7,
        "adult": 20,
        "reproduction_starts": 7,
        "total_cycle": 27,
        "vulnerable_stages": ["nymph"],
        "peak_damage_stage": "adult"
    }
}

# Chemical treatments database
CHEMICAL_TREATMENTS = {
    "Fall Armyworm": [
        {
            "product_name": "Emamectin Benzoate 5% SG",
            "active_ingredient": "Emamectin Benzoate",
            "dosage": "0.4 g/L water",
            "application_method": "Foliar spray",
            "rei_hours": 12,
            "phi_days": 7,
            "ppe_required": ["Gloves", "Mask", "Goggles", "Long sleeves"],
            "cost_per_hectare": 850.0,
            "approved_regions": ["India", "Generic"],
            "toxicity_class": "II (Moderately hazardous)",
            "severity_threshold": "Medium"
        },
        {
            "product_name": "Chlorantraniliprole 18.5% SC",
            "active_ingredient": "Chlorantraniliprole",
            "dosage": "0.3 mL/L water",
            "application_method": "Foliar spray",
            "rei_hours": 4,
            "phi_days": 3,
            "ppe_required": ["Gloves", "Mask"],
            "cost_per_hectare": 1200.0,
            "approved_regions": ["India", "Generic"],
            "toxicity_class": "U (Unlikely to present hazard)",
            "severity_threshold": "Low"
        },
        {
            "product_name": "Spinosad 45% SC",
            "active_ingredient": "Spinosad",
            "dosage": "0.5 mL/L water",
            "application_method": "Foliar spray",
            "rei_hours": 4,
            "phi_days": 1,
            "ppe_required": ["Gloves", "Mask"],
            "cost_per_hectare": 950.0,
            "approved_regions": ["India", "Generic"],
            "toxicity_class": "III (Slightly hazardous)",
            "severity_threshold": "High"
        }
    ],
    "Late Blight": [
        {
            "product_name": "Metalaxyl 8% + Mancozeb 64% WP",
            "active_ingredient": "Metalaxyl + Mancozeb",
            "dosage": "2.5 g/L water",
            "application_method": "Foliar spray",
            "rei_hours": 24,
            "phi_days": 14,
            "ppe_required": ["Gloves", "Mask", "Goggles", "Protective clothing"],
            "cost_per_hectare": 1100.0,
            "approved_regions": ["India", "Generic"],
            "toxicity_class": "II (Moderately hazardous)",
            "severity_threshold": "Medium"
        },
        {
            "product_name": "Cymoxanil 8% + Mancozeb 64% WP",
            "active_ingredient": "Cymoxanil + Mancozeb",
            "dosage": "2.0 g/L water",
            "application_method": "Foliar spray",
            "rei_hours": 24,
            "phi_days": 7,
            "ppe_required": ["Gloves", "Mask", "Goggles"],
            "cost_per_hectare": 980.0,
            "approved_regions": ["India", "Generic"],
            "toxicity_class": "II (Moderately hazardous)",
            "severity_threshold": "High"
        }
    ],
    "Aphids": [
        {
            "product_name": "Imidacloprid 17.8% SL",
            "active_ingredient": "Imidacloprid",
            "dosage": "0.3 mL/L water",
            "application_method": "Foliar spray",
            "rei_hours": 12,
            "phi_days": 7,
            "ppe_required": ["Gloves", "Mask"],
            "cost_per_hectare": 650.0,
            "approved_regions": ["India", "Generic"],
            "toxicity_class": "II (Moderately hazardous)",
            "severity_threshold": "Medium"
        },
        {
            "product_name": "Acetamiprid 20% SP",
            "active_ingredient": "Acetamiprid",
            "dosage": "0.2 g/L water",
            "application_method": "Foliar spray",
            "rei_hours": 12,
            "phi_days": 3,
            "ppe_required": ["Gloves", "Mask"],
            "cost_per_hectare": 720.0,
            "approved_regions": ["India", "Generic"],
            "toxicity_class": "III (Slightly hazardous)",
            "severity_threshold": "Low"
        }
    ]
}

# Organic/biological treatments
ORGANIC_TREATMENTS = {
    "Fall Armyworm": [
        {
            "method_name": "Neem Oil Spray",
            "materials": ["Neem oil (5 mL/L)", "Liquid soap (2 mL/L)", "Water"],
            "preparation_steps": [
                "Mix neem oil with liquid soap",
                "Add to water and stir thoroughly",
                "Let mixture sit for 10 minutes"
            ],
            "application_method": "Spray on affected plants during evening",
            "effectiveness_rating": 0.65,
            "cost_per_hectare": 450.0,
            "companion_plants": ["Marigold", "Sunflower", "Dill"]
        },
        {
            "method_name": "Bacillus thuringiensis (Bt) Spray",
            "materials": ["Bt var. kurstaki (2 g/L)", "Water", "Sticker (0.5 mL/L)"],
            "preparation_steps": [
                "Dissolve Bt powder in small amount of water",
                "Add to remaining water",
                "Add sticker and mix gently"
            ],
            "application_method": "Spray when larvae are young (1st-2nd instar)",
            "effectiveness_rating": 0.80,
            "cost_per_hectare": 600.0,
            "companion_plants": None
        },
        {
            "method_name": "Trichogramma Wasp Release",
            "materials": ["Trichogramma cards (50,000 wasps/hectare)"],
            "preparation_steps": [
                "Obtain fresh parasitoid cards (< 24 hours old)",
                "Release during early morning or evening"
            ],
            "application_method": "Distribute cards evenly across field, hang on plants",
            "effectiveness_rating": 0.72,
            "cost_per_hectare": 800.0,
            "companion_plants": ["Flowering plants to support wasps"]
        }
    ],
    "Late Blight": [
        {
            "method_name": "Bordeaux Mixture",
            "materials": ["Copper sulfate (100 g)", "Lime (100 g)", "Water (10 L)"],
            "preparation_steps": [
                "Dissolve copper sulfate in 5L water (container A)",
                "Mix lime in 5L water (container B)",
                "Slowly pour A into B while stirring"
            ],
            "application_method": "Protective spray before disease onset",
            "effectiveness_rating": 0.70,
            "cost_per_hectare": 550.0,
            "companion_plants": None
        },
        {
            "method_name": "Potassium Bicarbonate Spray",
            "materials": ["Potassium bicarbonate (5 g/L)", "Horticultural oil (5 mL/L)", "Water"],
            "preparation_steps": [
                "Mix potassium bicarbonate in water",
                "Add horticultural oil",
                "Shake well before use"
            ],
            "application_method": "Spray every 7-10 days as preventive",
            "effectiveness_rating": 0.60,
            "cost_per_hectare": 480.0,
            "companion_plants": None
        }
    ],
    "Aphids": [
        {
            "method_name": "Insecticidal Soap Spray",
            "materials": ["Pure castile soap (15 mL/L)", "Water"],
            "preparation_steps": [
                "Mix soap with water",
                "Ensure complete dissolution"
            ],
            "application_method": "Spray directly on aphids, repeat every 2-3 days",
            "effectiveness_rating": 0.68,
            "cost_per_hectare": 320.0,
            "companion_plants": ["Nasturtium", "Garlic", "Chives"]
        },
        {
            "method_name": "Ladybug Release",
            "materials": ["Ladybugs (1500-5000 per hectare)"],
            "preparation_steps": [
                "Lightly water plants before release",
                "Release during cool hours (evening)"
            ],
            "application_method": "Release beetles near aphid colonies",
            "effectiveness_rating": 0.85,
            "cost_per_hectare": 900.0,
            "companion_plants": ["Dill", "Fennel", "Yarrow"]
        },
        {
            "method_name": "Garlic-Chili Spray",
            "materials": ["Garlic cloves (100 g)", "Hot chili peppers (50 g)", "Water (1 L)", "Soap (5 mL)"],
            "preparation_steps": [
                "Blend garlic and chili with water",
                "Strain mixture",
                "Add soap and dilute 1:5 with water"
            ],
            "application_method": "Spray on affected areas every 3-4 days",
            "effectiveness_rating": 0.55,
            "cost_per_hectare": 280.0,
            "companion_plants": None
        }
    ]
}

# Cultural and mechanical practices
CULTURAL_PRACTICES = {
    "Fall Armyworm": [
        "Remove and destroy egg masses manually",
        "Deep plowing after harvest to expose pupae",
        "Intercrop with non-host plants (legumes)",
        "Use pheromone traps for monitoring (5-10 traps/hectare)",
        "Hand-pick larvae during early morning inspections",
        "Maintain field sanitation - remove crop residues"
    ],
    "Late Blight": [
        "Ensure proper plant spacing for air circulation",
        "Avoid overhead irrigation - use drip irrigation",
        "Remove infected plant parts immediately",
        "Destroy volunteer plants and cull piles",
        "Use disease-free certified seeds/tubers",
        "Hill up potato plants to protect tubers"
    ],
    "Aphids": [
        "Use reflective mulches (aluminum foil/silver plastic)",
        "Spray plants with strong water jet to dislodge aphids",
        "Remove heavily infested plant parts",
        "Avoid excessive nitrogen fertilization",
        "Install yellow sticky traps for monitoring",
        "Encourage natural predators (ladybugs, lacewings)"
    ]
}

# Severity thresholds (based on scientific literature)
SEVERITY_THRESHOLDS = {
    "Fall Armyworm": {
        "Low": {"lesion_pct_max": 10, "plants_affected_max": 20},
        "Medium": {"lesion_pct_max": 30, "plants_affected_max": 50},
        "High": {"lesion_pct_max": 60, "plants_affected_max": 75},
        "Critical": {"lesion_pct_max": 100, "plants_affected_max": 100}
    },
    "Late Blight": {
        "Low": {"lesion_pct_max": 5, "plants_affected_max": 10},
        "Medium": {"lesion_pct_max": 20, "plants_affected_max": 30},
        "High": {"lesion_pct_max": 50, "plants_affected_max": 60},
        "Critical": {"lesion_pct_max": 100, "plants_affected_max": 100}
    },
    "Aphids": {
        "Low": {"lesion_pct_max": 15, "plants_affected_max": 25},
        "Medium": {"lesion_pct_max": 40, "plants_affected_max": 50},
        "High": {"lesion_pct_max": 70, "plants_affected_max": 80},
        "Critical": {"lesion_pct_max": 100, "plants_affected_max": 100}
    }
}

# Economic impact multipliers (yield loss percentage by severity)
YIELD_LOSS_FACTORS = {
    "Fall Armyworm": {
        "Low": 0.08,      # 8% yield loss
        "Medium": 0.25,   # 25% yield loss
        "High": 0.55,     # 55% yield loss
        "Critical": 0.85  # 85% yield loss
    },
    "Late Blight": {
        "Low": 0.10,
        "Medium": 0.35,
        "High": 0.70,
        "Critical": 0.95
    },
    "Aphids": {
        "Low": 0.05,
        "Medium": 0.18,
        "High": 0.40,
        "Critical": 0.65
    }
}

# Environmental favorability factors
PEST_WEATHER_PREFERENCES = {
    "Fall Armyworm": {
        "optimal_temp_range": (25, 30),
        "optimal_humidity_range": (60, 80),
        "rainfall_preference": "moderate",
        "wind_sensitivity": "high"
    },
    "Late Blight": {
        "optimal_temp_range": (18, 24),
        "optimal_humidity_range": (85, 100),
        "rainfall_preference": "high",
        "wind_sensitivity": "medium"
    },
    "Aphids": {
        "optimal_temp_range": (20, 25),
        "optimal_humidity_range": (50, 70),
        "rainfall_preference": "low",
        "wind_sensitivity": "high"
    }
}