from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class PatientInput(BaseModel):
    request_id: Optional[UUID] = Field(
        default_factory=uuid4,
        description="Unique request ID for tracking predictions"
    )

    age: int = Field(
        ...,
        ge=0,
        le=120,
        description="Patient age in years"
    )

    gender: str = Field(
        ...,
        description="Patient gender (Male/Female/Other)"
    )

    heart_rate: int = Field(
        ...,
        ge=30,
        le=250,
        description="Heart rate in beats per minute"
    )

    systolic_bp: int = Field(
        ...,
        ge=50,
        le=250,
        description="Systolic blood pressure"
    )

    diastolic_bp: int = Field(
        ...,
        ge=30,
        le=200,
        description="Diastolic blood pressure"
    )

    temperature: float = Field(
        ...,
        ge=30.0,
        le=45.0,
        description="Body temperature in Celsius"
    )

    symptom: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Primary symptom described by patient"
    )

    history: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Relevant medical history"
    )

    # -----------------------------
    # Validators
    # -----------------------------

    @field_validator("gender")
    @classmethod
    def normalize_gender(cls, value: str) -> str:
        value = value.strip().capitalize()
        allowed = {"Male", "Female", "Other"}
        if value not in allowed:
            raise ValueError("Gender must be Male, Female, or Other")
        return value

    @field_validator("symptom", "history")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return value.strip().capitalize()


class PredictionResponse(BaseModel):
    risk_level: str = Field(
        ...,
        description="Predicted risk category (Low/Medium/High)"
    )

    department: str = Field(
        ...,
        description="Recommended hospital department"
    )

    explanation: List[str] = Field(
        ...,
        description="AI-generated explanation points"
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence score"
    )

    risk_probabilities: Dict[str, float] = Field(
        ...,
        description="Probability distribution across risk levels"
    )
