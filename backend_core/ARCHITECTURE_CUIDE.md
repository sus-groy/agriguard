# The Specialist - Architecture Guide

## 🏗️ System Overview

**The Specialist** is an AI-driven agricultural diagnostic engine designed using a **Core-First Strategy**. This means we've built the pure business logic first, completely isolated from API frameworks, databases, and frontend concerns.

### Philosophy

> "Data flows like water through pipes. The pipes (APIs, databases) can be replaced, but the flow logic stays constant."

This architecture separates:
- **What** the system does (business logic)
- **How** it communicates (API layer - not built yet)
- **Where** it stores data (database - not built yet)

---

## 📁 Directory Structure

```
backend_core/
│
├── models.py              # Data schemas (the "contract")
├── knowledge_base.py      # Static data (mock database)
├── logic.py              # Business rules (the "brain")
└── main_simulation.py    # Demo/testing script
```

### Why This Structure?

1. **models.py** - Defines what valid data looks like
   - Uses Python dataclasses for type safety
   - Acts as a contract between components
   - Changes here require updates everywhere (intentionally!)

2. **knowledge_base.py** - Separates data from logic
   - Currently: Static Python dictionaries
   - Future: Database queries
   - **Why separate?** Logic shouldn't care where data comes from

3. **logic.py** - Pure transformations
   - Input → Processing → Output
   - No I/O operations (no file reading, no API calls)
   - Fully testable in isolation

4. **main_simulation.py** - Proof of concept
   - Shows the system works end-to-end
   - Demonstrates realistic scenarios
   - Becomes your integration test suite later

---

## 🔄 Data Flow Explained

### The Journey of a Diagnostic Request

```
┌─────────────────────────────────────────────────────────────┐
│  1. INPUT (DiagnosticInput)                                 │
│     - Pest name: "Fall Armyworm"                            │
│     - Confidence: 0.92                                      │
│     - Lesion %: 15.5                                        │
│     - Growth stage: Vegetative                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. SEVERITY CALCULATION (logic.py)                         │
│     calculate_severity()                                    │
│     - Looks up thresholds in knowledge_base.py              │
│     - Applies growth stage multipliers                      │
│     - Returns: SeverityLevel.MEDIUM + risk factors          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. WEATHER CONTEXT (logic.py)                              │
│     mock_get_weather() → analyze_weather_risk()             │
│     - Gets weather data (mock for now)                      │
│     - Checks if conditions favor pest                       │
│     - Returns: WeatherContext with risk level               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. TREATMENT LOOKUP (logic.py)                             │
│     get_treatment_plan()                                    │
│     - Queries knowledge_base.py for treatments              │
│     - Filters by severity (no harsh chemicals for Low)      │
│     - Returns: Chemical + Organic + Cultural options        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. ECONOMIC ANALYSIS (logic.py)                            │
│     estimate_economic_risk()                                │
│     - Calculates potential yield loss                       │
│     - Compares treatment cost vs revenue loss               │
│     - Returns: ROI, break-even, recommendation              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. IPM SCHEDULE GENERATION (logic.py)                      │
│     generate_ipm_schedule()                                 │
│     - Creates day-by-day action plan                        │
│     - Considers pest lifecycle from knowledge_base.py       │
│     - Returns: Timeline with costs and materials            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  7. FINAL REPORT (FinalDiagnosticReport)                    │
│     - Aggregates all analyses                               │
│     - Adds emergency actions if needed                      │
│     - Includes confidence notes                             │
│     - Generates unique diagnostic ID                        │
└─────────────────────────────────────────────────────────────┘
```

### Key Insight: Immutable Data Flow

Each function receives input, processes it, and returns **new** output. Nothing is modified in place. This makes the system:
- **Testable**: Same input = same output
- **Debuggable**: You can inspect data at each step
- **Parallelizable**: No shared state means concurrent requests work

---

## 🧠 Why Separate Data from Logic?

### The Problem with Mixing

```python
# ❌ BAD: Logic mixed with data
def get_treatment(pest):
    if pest == "Fall Armyworm":
        return {
            "chemical": "Emamectin Benzoate",
            "dosage": "0.4 g/L",
            # ... 50 lines of data ...
        }
    elif pest == "Late Blight":
        # ... another 50 lines ...
```

**Issues:**
1. Logic file becomes 1000+ lines
2. Changing data requires modifying logic code
3. Can't easily update treatments without code changes
4. Testing requires loading all data every time

### The Solution: Separation

```python
# ✅ GOOD: Data in knowledge_base.py
CHEMICAL_TREATMENTS = {
    "Fall Armyworm": [
        {"product_name": "Emamectin Benzoate", ...},
        # More treatments
    ]
}

# ✅ GOOD: Logic in logic.py
def get_treatment(pest_name, severity):
    all_treatments = CHEMICAL_TREATMENTS.get(pest_name, [])
    return [t for t in all_treatments if meets_criteria(t, severity)]
```

**Benefits:**
1. Logic file stays focused on algorithms
2. Data can be updated independently
3. Easy to replace with database later (just change the import!)
4. Can mock data for testing

---

## 🔌 How to Replace Components Later

### Replacing Mock Weather API

**Current:**
```python
# logic.py
def mock_get_weather(location: str) -> Dict[str, float]:
    return {"temperature": 25.0, "humidity": 70.0}
```

**Production:**
```python
# weather_service.py (new file)
import requests

def get_weather(location: str) -> Dict[str, float]:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather",
        params={"q": location, "appid": api_key}
    )
    data = response.json()
    return {
        "temperature": data["main"]["temp"] - 273.15,  # Kelvin to Celsius
        "humidity": data["main"]["humidity"],
        "rainfall_7day": get_rainfall_forecast(location),  # Separate call
        "wind_speed": data["wind"]["speed"]
    }

# logic.py - just change the import!
from weather_service import get_weather as mock_get_weather
```

### Replacing Knowledge Base Dictionary

**Current:**
```python
# knowledge_base.py
CHEMICAL_TREATMENTS = {"Fall Armyworm": [...]}

# logic.py
from knowledge_base import CHEMICAL_TREATMENTS
chemicals = CHEMICAL_TREATMENTS.get(pest_name)
```

**Production (PostgreSQL):**
```python
# database.py (new file)
from sqlalchemy import create_engine, select
from models import ChemicalTreatmentDB  # ORM model

def get_chemical_treatments(pest_name: str) -> List[Dict]:
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        result = conn.execute(
            select(ChemicalTreatmentDB)
            .where(ChemicalTreatmentDB.pest_name == pest_name)
        )
        return [row._asdict() for row in result]

# logic.py - minimal change!
# from knowledge_base import CHEMICAL_TREATMENTS
from database import get_chemical_treatments as CHEMICAL_TREATMENTS
```

### The Pattern

**Before (Mock):**
```python
data = STATIC_DICT.get(key)
```

**After (Database):**
```python
data = query_database(key)  # Same interface, different source
```

The logic doesn't need to change because we designed it to accept data, not care where it comes from.

---

## 🧪 Testing Strategy

### Unit Tests (Test Each Function)

```python
# test_logic.py
import pytest
from logic import calculate_severity
from models import SeverityLevel, GrowthStage

def test_severity_calculation_low():
    severity, factors = calculate_severity(
        lesion_pct=8.0,
        pest_name="Fall Armyworm",
        confidence=0.9,
        growth_stage=GrowthStage.VEGETATIVE
    )
    assert severity == SeverityLevel.LOW
    assert len(factors) == 0  # No risk factors for low severity

def test_severity_calculation_high_at_flowering():
    severity, factors = calculate_severity(
        lesion_pct=25.0,  # Would be Medium normally
        pest_name="Fall Armyworm",
        confidence=0.9,
        growth_stage=GrowthStage.FLOWERING  # Bumps it up
    )
    assert severity == SeverityLevel.HIGH
    assert any("Critical growth stage" in f for f in factors)
```

### Integration Tests (Test Full Flow)

```python
# test_integration.py
def test_full_diagnostic_flow():
    input_data = DiagnosticInput(
        pest_name="Fall Armyworm",
        confidence=0.92,
        lesion_percentage=15.5,
        growth_stage=GrowthStage.VEGETATIVE,
        crop_type="Maize",
        crop_value_per_hectare=85000.0,
        location="Nagpur"
    )
    
    report = generate_diagnostic_report(input_data)
    
    assert report.diagnostic_id.startswith("DIAG-")
    assert report.severity_analysis.severity_level == SeverityLevel.MEDIUM
    assert len(report.treatment_plan.chemical_options) > 0
    assert report.economic_impact.roi_if_treated > 0
```

### Why This Works

Because logic is pure (no I/O), tests run:
- **Fast**: No database connections
- **Reliably**: No network calls
- **Deterministically**: Same input always gives same output

---

## 🚀 Next Steps for Production

### Phase 1: API Layer (Week 1-2)
1. Create `api/` folder with FastAPI endpoints
2. Define routes: `POST /diagnose`, `GET /report/{id}`
3. Validate input with Pydantic (already using similar patterns!)
4. Call `generate_diagnostic_report()` from endpoints

### Phase 2: Database Integration (Week 2-3)
1. Design PostgreSQL schema based on `models.py`
2. Create migration scripts
3. Replace `knowledge_base.py` imports with database queries
4. Add caching layer (Redis) for frequently accessed data

### Phase 3: External Services (Week 3-4)
1. Integrate OpenWeatherMap API
2. Add image storage (AWS S3/Cloudinary)
3. Implement notification service (SMS/Email)
4. Connect to agricultural advisory APIs

### Phase 4: Monitoring & Scaling (Week 4+)
1. Add logging (structured JSON logs)
2. Implement health checks
3. Set up metrics (Prometheus/Grafana)
4. Deploy with Docker + Kubernetes

---

## 🎯 Design Principles Applied

### 1. Separation of Concerns
- Data models don't know about business logic
- Business logic doesn't know about data sources
- API layer (future) won't know about internal calculations

### 2. Dependency Inversion
- `logic.py` depends on `models.py` (abstractions)
- `logic.py` does NOT depend on `knowledge_base.py` directly (imports it, but treats as plugin)
- This allows swapping knowledge_base.py with database.py

### 3. Single Responsibility
- Each function does ONE thing well
- `calculate_severity()` only calculates severity
- `get_treatment_plan()` only retrieves treatments
- Orchestration happens in `generate_diagnostic_report()`

### 4. Open/Closed Principle
- Open for extension: Add new pests by adding to `knowledge_base.py`
- Closed for modification: Core logic doesn't change

---

## 📚 Key Concepts for Team

### Dataclasses as Contracts

```python
@dataclass
class DiagnosticInput:
    pest_name: str
    confidence: float
    # ...
```

This means: "Any diagnostic MUST have these fields with these types."

If you try to create invalid data:
```python
DiagnosticInput(pest_name=123)  # ❌ TypeError!
```

### Type Hints Enable Tools

```python
def calculate_severity(
    lesion_pct: float,
    pest_name: str,
    confidence: float,
    growth_stage: GrowthStage
) -> Tuple[SeverityLevel, List[str]]:
```

Your IDE can:
- Auto-complete parameter names
- Warn if you pass wrong types
- Show expected return values

### Enums for Controlled Values

```python
class SeverityLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
```

Can't accidentally use `"low"` vs `"Low"` vs `"LOW"` - only valid enum values work.

---

## 🔍 Common Questions

**Q: Why not just use a database from the start?**

A: Building logic first lets you:
1. Iterate quickly without migration scripts
2. Test without database setup
3. Understand data requirements before schema design
4. Deploy as serverless functions easily (no DB connection overhead)

**Q: Isn't mock data unrealistic?**

A: The mock data is based on real agricultural research. It's simplified, but accurate enough to build and test logic. Production data will follow the same structure.

**Q: How do I add a new pest?**

A: 
1. Add entry to `PEST_LIFECYCLES` in `knowledge_base.py`
2. Add chemical treatments to `CHEMICAL_TREATMENTS`
3. Add organic treatments to `ORGANIC_TREATMENTS`
4. Add cultural practices to `CULTURAL_PRACTICES`
5. Run simulation to verify it works!

No code changes needed in `logic.py` - it automatically handles any pest in the knowledge base.

---

## 📖 Further Reading

- **Martin Fowler - Dependency Injection**: Understanding why separating concerns matters
- **Clean Architecture (Robert Martin)**: The principles behind this design
- **Python Type Hints (PEP 484)**: Why we use type annotations extensively

---

## 🎓 Learning Path for New Developers

1. **Day 1**: Read this guide, run `main_simulation.py`
2. **Day 2**: Study `models.py` - understand the data structures
3. **Day 3**: Read `knowledge_base.py` - see what data we have
4. **Day 4**: Trace through `logic.py` for one function (e.g., `calculate_severity`)
5. **Day 5**: Trace through `generate_diagnostic_report()` - see the full flow
6. **Week 2**: Write tests for individual functions
7. **Week 3**: Add a new pest to the knowledge base
8. **Week 4**: Ready to build API endpoints!

---

*Last Updated: 2026-01-13*  
*Version: 1.0 (Core Backend Only)*