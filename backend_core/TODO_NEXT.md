# TODO: Production Integration Checklist

## 🎯 Overview

This document lists exactly what needs to be replaced to move from the current **mock/simulation** version to a **production-ready** system.

Each item includes:
- ✅ **What to replace**
- 🔧 **How to replace it**
- 💡 **Code snippets or hints**
- ⚠️ **Gotchas to watch out for**

---

## 📦 Phase 1: Database Integration

### 1.1 Replace `knowledge_base.py` with PostgreSQL

**Current State:**
```python
# knowledge_base.py
CHEMICAL_TREATMENTS = {
    "Fall Armyworm": [
        {"product_name": "Emamectin Benzoate", ...}
    ]
}
```

**Target State:** Store all treatments, pests, and practices in relational database.

**Steps:**

1. **Create Database Schema**

```sql
-- migrations/001_create_pests_table.sql
CREATE TABLE pests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(200),
    lifecycle_data JSONB,  -- Store lifecycle stages
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chemical_treatments (
    id SERIAL PRIMARY KEY,
    pest_id INTEGER REFERENCES pests(id),
    product_name VARCHAR(200) NOT NULL,
    active_ingredient VARCHAR(200),
    dosage VARCHAR(100),
    application_method TEXT,
    rei_hours INTEGER,
    phi_days INTEGER,
    ppe_required JSONB,  -- Array of PPE items
    cost_per_hectare DECIMAL(10, 2),
    approved_regions JSONB,
    toxicity_class VARCHAR(50),
    severity_threshold VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE organic_treatments (
    id SERIAL PRIMARY KEY,
    pest_id INTEGER REFERENCES pests(id),
    method_name VARCHAR(200) NOT NULL,
    materials JSONB,
    preparation_steps JSONB,
    application_method TEXT,
    effectiveness_rating DECIMAL(3, 2),
    cost_per_hectare DECIMAL(10, 2),
    companion_plants JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE cultural_practices (
    id SERIAL PRIMARY KEY,
    pest_id INTEGER REFERENCES pests(id),
    practice_description TEXT NOT NULL,
    priority_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for common queries
CREATE INDEX idx_chemical_pest ON chemical_treatments(pest_id);
CREATE INDEX idx_organic_pest ON organic_treatments(pest_id);
CREATE INDEX idx_cultural_pest ON cultural_practices(pest_id);
```

2. **Create Data Access Layer**

```python
# database/repositories.py
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/specialist")
engine = create_engine(DATABASE_URL)

class TreatmentRepository:
    """Data access for pest treatments"""
    
    def get_chemical_treatments(self, pest_name: str, severity: str) -> List[Dict]:
        """
        Fetch chemical treatments for a pest filtered by severity.
        
        Args:
            pest_name: Name of pest/disease
            severity: Current severity level (Low/Medium/High/Critical)
        
        Returns:
            List of chemical treatment dictionaries
        """
        with Session(engine) as session:
            # Get pest ID first
            pest = session.execute(
                select(Pest).where(Pest.name == pest_name)
            ).scalar_one_or_none()
            
            if not pest:
                return []
            
            # Fetch treatments
            treatments = session.execute(
                select(ChemicalTreatment)
                .where(ChemicalTreatment.pest_id == pest.id)
                .where(ChemicalTreatment.severity_threshold <= severity)  # Filter by severity
            ).scalars().all()
            
            return [self._treatment_to_dict(t) for t in treatments]
    
    def _treatment_to_dict(self, treatment) -> Dict:
        """Convert ORM object to dictionary matching current structure"""
        return {
            "product_name": treatment.product_name,
            "active_ingredient": treatment.active_ingredient,
            "dosage": treatment.dosage,
            "application_method": treatment.application_method,
            "rei_hours": treatment.rei_hours,
            "phi_days": treatment.phi_days,
            "ppe_required": treatment.ppe_required,
            "cost_per_hectare": float(treatment.cost_per_hectare),
            "approved_regions": treatment.approved_regions,
            "toxicity_class": treatment.toxicity_class,
            "severity_threshold": treatment.severity_threshold
        }
    
    def get_organic_treatments(self, pest_name: str) -> List[Dict]:
        """Fetch organic treatments for a pest"""
        # Similar implementation...
        pass
```

3. **Update `logic.py` to Use Repository**

```python
# logic.py - OLD
from knowledge_base import CHEMICAL_TREATMENTS

def get_treatment_plan(pest_name, severity, location):
    all_chemicals = CHEMICAL_TREATMENTS.get(pest_name, [])
    # ...

# logic.py - NEW
from database.repositories import TreatmentRepository

_treatment_repo = TreatmentRepository()  # Singleton or inject via DI

def get_treatment_plan(pest_name, severity, location):
    all_chemicals = _treatment_repo.get_chemical_treatments(pest_name, severity.value)
    # Rest of the logic stays the same!
```

**⚠️ Gotchas:**
- Don't forget connection pooling for production
- Use environment variables for credentials (never hardcode!)
- Add retry logic for transient database errors
- Consider read replicas for scaling

---

### 1.2 Migrate Static Data to Database

**Script to populate database from current dictionaries:**

```python
# migrations/seed_data.py
from database.repositories import TreatmentRepository
from knowledge_base import (
    CHEMICAL_TREATMENTS, ORGANIC_TREATMENTS, 
    CULTURAL_PRACTICES, PEST_LIFECYCLES
)

def migrate_knowledge_base():
    """One-time migration of mock data to database"""
    repo = TreatmentRepository()
    
    for pest_name, lifecycle in PEST_LIFECYCLES.items():
        # Insert pest
        pest_id = repo.create_pest(
            name=pest_name,
            lifecycle_data=lifecycle
        )
        
        # Insert chemical treatments
        for chem in CHEMICAL_TREATMENTS.get(pest_name, []):
            repo.create_chemical_treatment(pest_id, chem)
        
        # Insert organic treatments
        for org in ORGANIC_TREATMENTS.get(pest_name, []):
            repo.create_organic_treatment(pest_id, org)
        
        # Insert cultural practices
        for practice in CULTURAL_PRACTICES.get(pest_name, []):
            repo.create_cultural_practice(pest_id, practice)
    
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate_knowledge_base()
```

---

## 🌦️ Phase 2: External API Integration

### 2.1 Replace `mock_get_weather()` with Real Weather API

**Current:**
```python
# logic.py
def mock_get_weather(location: str) -> Dict[str, float]:
    return {"temperature": 25.0, "humidity": 70.0}
```

**Production:**

1. **Choose a Weather Service:**
   - OpenWeatherMap (Free tier: 1000 calls/day)
   - Weather API (Free tier: 1M calls/month)
   - Visual Crossing (Free tier: 1000 calls/day)

2. **Create Weather Service Module:**

```python
# services/weather_service.py
import requests
import os
from typing import Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    """Production weather data fetching"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable required")
        
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location: str) -> Dict[str, float]:
        """
        Fetch current weather for location.
        
        Args:
            location: City name (e.g., "Nagpur,IN" or "Mumbai")
        
        Returns:
            Weather data dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"  # Celsius
                },
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Get 7-day rainfall from forecast API
            rainfall = self._get_7day_rainfall(location)
            
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "rainfall_7day": rainfall,
                "wind_speed": data["wind"]["speed"] * 3.6  # m/s to km/h
            }
        
        except requests.RequestException as e:
            logger.error(f"Weather API error for {location}: {e}")
            # Fallback to cached data or reasonable defaults
            return self._get_fallback_weather(location)
    
    def _get_7day_rainfall(self, location: str) -> float:
        """Fetch 7-day rainfall forecast"""
        try:
            response = requests.get(
                f"{self.base_url}/forecast",
                params={
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            # Sum rainfall from forecast (API gives 5-day, 3-hour intervals)
            total_rain = sum(
                item.get("rain", {}).get("3h", 0) 
                for item in data.get("list", [])[:56]  # 7 days * 8 intervals
            )
            return total_rain
        
        except Exception as e:
            logger.warning(f"Rainfall forecast unavailable: {e}")
            return 0.0
    
    def _get_fallback_weather(self, location: str) -> Dict[str, float]:
        """Return sensible defaults if API fails"""
        # Could query cached data from database here
        logger.warning(f"Using fallback weather for {location}")
        return {
            "temperature": 25.0,
            "humidity": 70.0,
            "rainfall_7day": 10.0,
            "wind_speed": 5.0
        }

# Singleton instance
_weather_service = WeatherService()

def get_weather(location: str) -> Dict[str, float]:
    """Public interface matching mock signature"""
    return _weather_service.get_current_weather(location)
```

3. **Update logic.py:**

```python
# logic.py - OLD
def mock_get_weather(location: str) -> Dict[str, float]:
    # ...

# logic.py - NEW
from services.weather_service import get_weather as mock_get_weather
# The rest of the code stays EXACTLY the same!
```

**⚠️ Gotchas:**
- Rate limiting: Cache results for at least 10 minutes
- API failures: Always have fallback data
- Location parsing: "Nagpur" vs "Nagpur, Maharashtra" vs coordinates
- Cost monitoring: Track API calls to avoid overage charges

---

### 2.2 Add Caching Layer

**Why:** Weather doesn't change every second. Avoid redundant API calls.

```python
# services/cache.py
import redis
import json
from typing import Optional, Dict
import os

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

class WeatherCache:
    """Cache weather data in Redis"""
    
    CACHE_TTL = 600  # 10 minutes
    
    @staticmethod
    def get(location: str) -> Optional[Dict[str, float]]:
        """Get cached weather data"""
        key = f"weather:{location}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    @staticmethod
    def set(location: str, weather_data: Dict[str, float]):
        """Cache weather data"""
        key = f"weather:{location}"
        redis_client.setex(
            key,
            WeatherCache.CACHE_TTL,
            json.dumps(weather_data)
        )

# Update weather service to use cache
class WeatherService:
    def get_current_weather(self, location: str) -> Dict[str, float]:
        # Check cache first
        cached = WeatherCache.get(location)
        if cached:
            logger.info(f"Cache hit for {location}")
            return cached
        
        # Fetch from API
        weather_data = self._fetch_from_api(location)
        
        # Store in cache
        WeatherCache.set(location, weather_data)
        
        return weather_data
```

---

## 📊 Phase 3: Diagnostic History & Reporting

### 3.1 Store Diagnostic Reports

**Why:** Track diagnoses over time for analytics, ML training, and user history.

**Database Schema:**

```sql
-- migrations/003_create_diagnostics.sql
CREATE TABLE diagnostic_reports (
    id SERIAL PRIMARY KEY,
    diagnostic_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER,  -- If you have user system
    
    -- Input data
    pest_name VARCHAR(100) NOT NULL,
    confidence DECIMAL(4, 3),
    lesion_percentage DECIMAL(5, 2),
    growth_stage VARCHAR(50),
    crop_type VARCHAR(100),
    crop_value_per_hectare DECIMAL(12, 2),
    location VARCHAR(200),
    
    -- Analysis results
    severity_level VARCHAR(20),
    estimated_revenue_loss DECIMAL(12, 2),
    treatment_cost_min DECIMAL(10, 2),
    treatment_cost_max DECIMAL(10, 2),
    roi_if_treated DECIMAL(8, 2),
    
    -- Full report as JSON (for detailed retrieval)
    full_report JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_diagnostic_user ON diagnostic_reports(user_id);
CREATE INDEX idx_diagnostic_date ON diagnostic_reports(created_at);
CREATE INDEX idx_diagnostic_pest ON diagnostic_reports(pest_name);
```

**Repository Method:**

```python
# database/repositories.py
class DiagnosticRepository:
    def save_report(self, report: FinalDiagnosticReport) -> str:
        """
        Save diagnostic report to database.
        
        Returns:
            Diagnostic ID
        """
        with Session(engine) as session:
            db_report = DiagnosticReportModel(
                diagnostic_id=report.diagnostic_id,
                pest_name=report.input_data.pest_name,
                confidence=report.input_data.confidence,
                lesion_percentage=report.input_data.lesion_percentage,
                growth_stage=report.input_data.growth_stage.value,
                crop_type=report.input_data.crop_type,
                crop_value_per_hectare=report.input_data.crop_value_per_hectare,
                location=report.input_data.location,
                severity_level=report.severity_analysis.severity_level.value,
                estimated_revenue_loss=report.economic_impact.estimated_revenue_loss,
                treatment_cost_min=report.economic_impact.treatment_cost_range["min"],
                treatment_cost_max=report.economic_impact.treatment_cost_range["max"],
                roi_if_treated=report.economic_impact.roi_if_treated,
                full_report=self._report_to_json(report)
            )
            session.add(db_report)
            session.commit()
            
            return report.diagnostic_id
    
    def get_report(self, diagnostic_id: str) -> Optional[FinalDiagnosticReport]:
        """Retrieve report by ID"""
        # Query and reconstruct from JSON...
```

**Update Main Flow:**

```python
# logic.py
def generate_diagnostic_report(diagnostic_input: DiagnosticInput) -> FinalDiagnosticReport:
    # ... existing logic ...
    
    report = FinalDiagnosticReport(...)
    
    # Save to database (in production)
    if os.getenv("ENV") == "production":
        from database.repositories import DiagnosticRepository
        repo = DiagnosticRepository()
        repo.save_report(report)
    
    return report
```

---

## 🔐 Phase 4: API Layer (FastAPI)

### 4.1 Create FastAPI Endpoints

**Directory Structure:**
```
api/
├── main.py           # FastAPI app
├── routes/
│   ├── diagnostic.py  # Diagnosis endpoints
│   └── reports.py     # Report retrieval
├── schemas.py        # Pydantic request/response models
└── dependencies.py   # Shared dependencies
```

**Example Implementation:**

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import diagnostic, reports

app = FastAPI(
    title="The Specialist API",
    description="Agricultural Diagnostic Engine",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnostic.router, prefix="/api/v1", tags=["diagnostic"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

```python
# api/routes/diagnostic.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

from models import DiagnosticInput, GrowthStage
from logic import generate_diagnostic_report

router = APIRouter()

class DiagnosticRequest(BaseModel):
    """API request schema"""
    pest_name: str = Field(..., example="Fall Armyworm")
    confidence: float = Field(..., ge=0.0, le=1.0, example=0.92)
    lesion_percentage: float = Field(..., ge=0.0, le=100.0, example=15.5)
    growth_stage: str = Field(..., example="Vegetative")
    crop_type: str = Field(..., example="Maize")
    crop_value_per_hectare: float = Field(..., gt=0, example=85000.0)
    location: str = Field(..., example="Nagpur, India")
    visual_symptoms: List[str] = Field(default_factory=list)

@router.post("/diagnose")
async def create_diagnosis(request: DiagnosticRequest):
    """
    Perform agricultural pest/disease diagnosis.
    
    Returns complete IPM plan with economic analysis.
    """
    try:
        # Convert API request to internal model
        diagnostic_input = DiagnosticInput(
            pest_name=request.pest_name,
            confidence=request.confidence,
            lesion_percentage=request.lesion_percentage,
            growth_stage=GrowthStage(request.growth_stage),
            crop_type=request.crop_type,
            crop_value_per_hectare=request.crop_value_per_hectare,
            location=request.location,
            visual_symptoms=request.visual_symptoms,
            detection_timestamp=datetime.now()
        )
        
        # Generate report (core logic unchanged!)
        report = generate_diagnostic_report(diagnostic_input)
        
        # Convert to JSON response
        return {
            "diagnostic_id": report.diagnostic_id,
            "timestamp": report.timestamp.isoformat(),
            "severity": report.severity_analysis.severity_level.value,
            "economic_impact": {
                "revenue_loss": report.economic_impact.estimated_revenue_loss,
                "treatment_cost": report.economic_impact.treatment_cost_range,
                "roi": report.economic_impact.roi_if_treated,
                "recommendation": report.economic_impact.recommendation
            },
            "treatment_plan": {
                "primary_strategy": report.treatment_plan.primary_strategy.value,
                "chemical_options": [
                    {
                        "name": c.product_name,
                        "dosage": c.dosage,
                        "cost": c.cost_per_hectare,
                        "phi_days": c.phi_days
                    } for c in report.treatment_plan.chemical_options
                ],
                "organic_options": [
                    {
                        "name": o.method_name,
                        "effectiveness": o.effectiveness_rating,
                        "cost": o.cost_per_hectare
                    } for o in report.treatment_plan.organic_options
                ],
                "schedule": [
                    {
                        "day": s.day,
                        "action": s.action_type,
                        "description": s.description,
                        "cost": s.estimated_cost
                    } for s in report.treatment_plan.ipm_timeline
                ]
            },
            "emergency_actions": report.emergency_actions,
            "confidence_notes": report.confidence_notes
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log error
        raise HTTPException(status_code=500, detail="Internal server error")
```

**⚠️ Gotchas:**
- Validate input strictly (Pydantic helps!)
- Return user-friendly errors (not stack traces)
- Add rate limiting to prevent abuse
- Version your API (`/api/v1/`) for backward compatibility

---

## 🖼️ Phase 5: Image Processing Integration

### 5.1 Add Image Upload & Storage

**Current:** We receive pre-processed pest names and confidence scores.

**Production:** Accept raw images, run through ML model, extract pest info.

**Storage Solution:**

```python
# services/image_storage.py
import boto3
from typing import Tuple
import os
import uuid

class ImageStorage:
    """Handle image uploads to AWS S3"""
    
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )
        self.bucket = os.getenv('S3_BUCKET_NAME')
    
    def upload_diagnostic_image(
        self, 
        image_data: bytes, 
        diagnostic_id: str
    ) -> str:
        """
        Upload image to S3 and return URL.
        
        Args:
            image_data: Raw image bytes
            diagnostic_id: Associated diagnostic ID
        
        Returns:
            Public URL of uploaded image
        """
        filename = f"diagnostics/{diagnostic_id}/{uuid.uuid4()}.jpg"
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=image_data,
            ContentType='image/jpeg',
            ACL='private'  # Use presigned URLs for access
        )
        
        # Generate presigned URL (expires in 7 days)
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': filename},
            ExpiresIn=604800
        )
        
        return url
```

**ML Model Integration:**

```python
# services/pest_detector.py
import torch
from PIL import Image
import io

class PestDetector:
    """Run pest detection on images"""
    
    def __init__(self):
        # Load your trained model
        self.model = torch.load('models/pest_detector_v1.pth')
        self.model.eval()
    
    def detect_pest(self, image_data: bytes) -> Tuple[str, float, float]:
        """
        Detect pest from image.
        
        Returns:
            (pest_name, confidence, lesion_percentage)
        """
        # Preprocess image
        image = Image.open(io.BytesIO(image_data))
        tensor = self._preprocess(image)
        
        # Run inference
        with torch.no_grad():
            output = self.model(tensor)
        
        # Parse results
        pest_name = self._get_pest_name(output)
        confidence = float(output.max())
        lesion_pct = self._calculate_lesion_area(image, output)
        
        return pest_name, confidence, lesion_pct
```

**Update API Endpoint:**

```python
# api/routes/diagnostic.py
from fastapi import File, UploadFile

@router.post("/diagnose/image")
async def diagnose_from_image(
    image: UploadFile = File(...),
    crop_type: str = "Unknown",
    location: str = "Unknown"
):
    """Diagnose pest from uploaded image"""
    
    # Read image
    image_data = await image.read()
    
    # Run ML detection
    detector = PestDetector()
    pest_name, confidence, lesion_pct = detector.detect_pest(image_data)
    
    # Store image
    diagnostic_id = f"DIAG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4()}"
    storage = ImageStorage()
    image_url = storage.upload_diagnostic_image(image_data, diagnostic_id)
    
    # Continue with normal diagnostic flow...
    diagnostic_input = DiagnosticInput(
        pest_name=pest_name,
        confidence=confidence,
        lesion_percentage=lesion_pct,
        # ... rest of fields
    )
    
    report = generate_diagnostic_report(diagnostic_input)
    
    return {
        "image_url": image_url,
        **report
    }
```

---

## 📈 Phase 6: Monitoring & Logging

### 6.1 Add Structured Logging

```python
# utils/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing"""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)

# Setup
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
```

### 6.2 Add Performance Metrics

```python
# utils/metrics.py
from prometheus_client import Counter, Histogram
import time

# Define metrics
diagnostic_requests = Counter(
    'diagnostic_requests_total',
    'Total diagnostic requests',
    ['pest_name', 'severity']
)

diagnostic_duration = Histogram(
    'diagnostic_duration_seconds',
    'Time to complete diagnosis'
)

# Use in code
def generate_diagnostic_report(diagnostic_input):
    start_time = time.time()
    
    # ... existing logic ...
    
    report = FinalDiagnosticReport(...)
    
    # Record metrics
    diagnostic_requests.labels(
        pest_name=diagnostic_input.pest_name,
        severity=report.severity_analysis.severity_level.value
    ).inc()
    
    duration = time.time() - start_time
    diagnostic_duration.observe(duration)
    
    return report
```

---

## ✅ Priority Order

Do these in order for maximum value with minimum risk:

1. **Week 1: Database Integration** (Highest Priority)
   - [ ] Set up PostgreSQL
   - [ ] Create schema
   - [ ] Migrate knowledge_base data
   - [ ] Update logic.py to use DB

2. **Week 2: API Layer** 
   - [ ] Build FastAPI endpoints
   - [ ] Add input validation
   - [ ] Test with Postman/curl
   - [ ] Deploy to staging

3. **Week 3: External Services**
   - [ ] Integrate weather API
   - [ ] Add caching (Redis)
   - [ ] Set up monitoring
   - [ ] Add logging

4. **Week 4: Image Processing**
   - [ ] Set up S3 storage
   - [ ] Integrate ML model
   - [ ] Add image endpoint
   - [ ] Test end-to-end

5. **Week 5+: Polish & Scale**
   - [ ] Add authentication
   - [ ] Rate limiting
   - [ ] Analytics dashboard
   - [ ] Load testing

---

## 🚨 Critical Reminders

1. **Always use environment variables for secrets**
   ```python
   # ❌ NEVER
   API_KEY = "abc123xyz"
   
   # ✅ ALWAYS
   API_KEY = os.getenv("OPENWEATHER_API_KEY")
   if not API_KEY:
       raise ValueError("API key required!")
   ```

2. **Add error handling everywhere**
   ```python
   try:
       weather = get_weather(location)
   except RequestException:
       weather = get_cached_weather(location)
   except Exception as e:
       logger.error(f"Weather fetch failed: {e}")
       weather = default_weather()
   ```

3. **Test before replacing**
   - Keep `knowledge_base.py` alongside database initially
   - Use feature flags to toggle between mock and real
   - Compare outputs to ensure consistency

4. **Document as you go**
   - Update this TODO with completion dates
   - Note any issues encountered
   - Share learnings with team

---

## 📝 Completion Tracking

Mark items as complete:

- [ ] PostgreSQL setup
- [ ] Data migration
- [ ] Weather API integration
- [ ] Caching layer
- [ ] FastAPI endpoints
- [ ] Image storage
- [ ] ML model integration
- [ ] Logging & monitoring
- [ ] Authentication
- [ ] Production deployment

**Target Completion:** 2026-02-15

---

*Last Updated: 2026-01-13*  
*Keep this document updated as you progress!*