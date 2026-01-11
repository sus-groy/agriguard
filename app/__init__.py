"""Agricultural Diagnostic Engine - Application Package"""

from .core import (
    DiagnosticResult,
    ScoringEngine,
    ChemicalDatabase,
    Region,
    UrgencyLevel,
    SeverityLevel,
)

from .services import (
    GeminiDiagnosticClient,
    generate_diagnostic_prompt,
)

__version__ = "1.0.0"
__all__ = [
    "DiagnosticResult",
    "ScoringEngine",
    "ChemicalDatabase",
    "Region",
    "UrgencyLevel",
    "SeverityLevel",
    "GeminiDiagnosticClient",
    "generate_diagnostic_prompt",
]
