# Agricultural Diagnostic Engine

AI-powered pest and disease diagnosis for crops using Google Gemini Vision API.

## Quick Start

### Prerequisites

- Python 3.8+
- pip or conda
- Google API Key (from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone or download this project:**
```bash
cd BuildwithGemini
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set environment variable for Gemini API:**
```bash
export GOOGLE_API_KEY=your_api_key_here
# On Windows:
set GOOGLE_API_KEY=your_api_key_here
```

### Running the API Server

```bash
uvicorn app.main:app --reload
```

Server runs at: **http://localhost:8000**

Interactive API docs: **http://localhost:8000/docs**

### Testing the System

**Run integration tests and examples:**
```bash
python -m app.tests.integration_demo
```

**Test API endpoint with curl:**
```bash
curl -X POST http://localhost:8000/diagnose \
  -F "file=@sample_image.jpg" \
  -F "crop_type=tomato" \
  -F "region=NORTH_AMERICA"
```

## Project Structure

```
app/
├── core/              # Business logic (models, scoring, database)
├── services/          # External integrations (Gemini API)
├── tests/             # Demo and integration tests
└── main.py            # FastAPI application
```

## Key Features

✅ **Vision-based diagnosis** - Analyzes crop images with Gemini 2.0 Flash  
✅ **Confidence scoring** - Combines VLM probability with evidence validation  
✅ **Safety-verified database** - Non-LLM treatments with PPE requirements  
✅ **Multi-region support** - Region-specific chemical restrictions  
✅ **RESTful API** - Easy integration with web/mobile apps  

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/diagnose` | Analyze crop image and return diagnosis |
| GET | `/health` | Health check |
| GET | `/pests` | List all pests in database |
| GET | `/pests/{name}` | Get treatments for specific pest |
| GET | `/schema` | JSON schema for DiagnosticResult |

## Documentation

- **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** - Complete technical reference with API details, data models, configuration, and examples
- **[app/core/models.py](app/core/models.py)** - All Pydantic models and enums
- **[app/core/scoring.py](app/core/scoring.py)** - Scoring engine logic
- **[app/core/chemical_db.py](app/core/chemical_db.py)** - Chemical database with treatments
- **[app/services/gemini.py](app/services/gemini.py)** - Gemini Vision API integration

## Example Usage

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Check health
response = client.get("/health")
print(response.json())

# Diagnose crop image
with open("crop_image.jpg", "rb") as f:
    response = client.post(
        "/diagnose",
        files={"file": f},
        data={"crop_type": "tomato", "region": "NORTH_AMERICA"}
    )
    result = response.json()
    print(f"Pest: {result['diagnosis']['label']}")
    print(f"Confidence: {result['confidence_overall']:.1%}")
```

## Supported Crops & Pests

**Tomato:** Early Blight, Powdery Mildew  
**Potato:** Colorado Potato Beetle, Late Blight  
**Corn:** Corn Earworm, Leaf Spots  
**Wheat:** Wheat Rust, Powdery Mildew  
**Lettuce:** Lettuce Downy Mildew, Leaf Diseases  

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GOOGLE_API_KEY not set` | Set environment variable: `export GOOGLE_API_KEY=...` |
| `Module not found` | Run: `pip install -r requirements.txt` |
| `Port 8000 already in use` | Run: `uvicorn app.main:app --port 8001` |
| `Image processing error` | Ensure image is JPEG/PNG and under 5MB |

## Requirements

See [requirements.txt](requirements.txt) for full dependency list:
- fastapi
- uvicorn
- pydantic
- pillow
- google-generativeai
- python-multipart

## Development

### Architecture Principles

- **Core Logic Isolated** - Business logic in `app/core/` has no external dependencies
- **Services Decoupled** - External APIs (Gemini) in `app/services/` can be swapped
- **Type Safety** - All models validated with Pydantic v2
- **Non-LLM Scoring** - Sensitive calculations use deterministic algorithms

### Running Tests

```bash
# Integration demo
python -m app.tests.integration_demo

# With pytest (if installed)
pytest app/tests/
```

### Adding New Treatments

Edit [app/core/chemical_db.py](app/core/chemical_db.py) and add to `self.database` dictionary. All treatments should include:
- Product name
- Active ingredient
- Dosage
- Application frequency
- PPE requirements
- Pre-harvest interval
- Regional restrictions

## Support

For detailed technical information, see [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md).

---

**Version:** 1.0.0  
**Last Updated:** 2024
