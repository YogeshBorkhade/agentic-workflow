"""
Evaluation & Metrics Layer
Version 1.0.0
"""

from .evaluation import (
    # Core classes
    LLMJudge,
    SelfAssessment,
    MetricsTracker,
    EvaluationPipeline,
    
    # Data models
    EvaluationResult,
    PerformanceMetrics,
    
    # Enums
    EvaluationMethod,
    QualityCriteria
)

__version__ = "1.0.0"

__all__ = [
    "LLMJudge",
    "SelfAssessment",
    "MetricsTracker",
    "EvaluationPipeline",
    "EvaluationResult",
    "PerformanceMetrics",
    "EvaluationMethod",
    "QualityCriteria"
]