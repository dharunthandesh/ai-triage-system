from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from supabase_client import supabase

import joblib
import pandas as pd
from datetime import datetime
from schemas import PatientInput, PredictionResponse
import logging

from priority import calculate_priority, get_priority_level  # if using request schemas
# other imports you already have

app = FastAPI()

# -----------------------------
# Logger Setup
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="Smart Patient Triage API")

# @app.get("/")
# def root():
#     return {"message": "AI Triage Backend Running 🚀"}

# -----------------------------
# Load Model Artifacts
# -----------------------------
try:
    artifacts = joblib.load("triage_model.joblib")

    risk_model = artifacts["risk_model"]
    dept_model = artifacts["dept_model"]
    le_gender = artifacts["le_gender"]
    le_symptom = artifacts["le_symptom"]
    le_history = artifacts["le_history"]
    le_risk = artifacts["le_risk"]
    le_dept = artifacts["le_dept"]

    logger.info("✅ Model loaded successfully.")

except Exception as e:
    logger.error(f"❌ Error loading model: {e}")
    risk_model = None
    dept_model = None

# -----------------------------
# Configure CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Utility: Safe LabelEncoder transform
# -----------------------------
def safe_transform(le, value):
    if value in le.classes_:
        return le.transform([value])[0]
    else:
        # Unknown value, use a special unknown index (-1)
        return -1

# -----------------------------
# Prediction Endpoint
# -----------------------------
@app.post("/api/predict", response_model=PredictionResponse)
def predict_triage(patient: PatientInput):

    if risk_model is None or dept_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Encode Inputs safely
        gender_encoded = safe_transform(le_gender, patient.gender)
        symptom_encoded = safe_transform(le_symptom, patient.symptom)
        history_encoded = safe_transform(le_history, patient.history)

        # Feature DataFrame
        features = pd.DataFrame([{
            "Age": patient.age,
            "Gender_Encoded": gender_encoded,
            "Heart Rate": patient.heart_rate,
            "Systolic BP": patient.systolic_bp,
            "Diastolic BP": patient.diastolic_bp,
            "Temperature": patient.temperature,
            "Symptom_Encoded": symptom_encoded,
            "History_Encoded": history_encoded
        }])

        # Predictions
        risk_encoded = risk_model.predict(features)[0]
        dept_encoded = dept_model.predict(features)[0]

        risk_level = le_risk.inverse_transform([risk_encoded])[0]
        department = le_dept.inverse_transform([dept_encoded])[0]

        risk_proba_raw = risk_model.predict_proba(features)[0]
        dept_proba_raw = dept_model.predict_proba(features)[0]

        risk_proba = float(max(risk_proba_raw))
        dept_proba = float(max(dept_proba_raw))

        # Risk probability breakdown
        risk_probs = {
            cls: float(prob)
            for cls, prob in zip(le_risk.classes_, risk_proba_raw)
        }

        # Explanation
        explanation = [
            f"Patient has {patient.symptom} with {patient.history} history."
        ]
        if patient.temperature > 38.0:
            explanation.append(f"Elevated temperature ({patient.temperature}°C) indicates potential infection.")
        if patient.heart_rate > 100:
            explanation.append(f"Tachycardia detected (HR: {patient.heart_rate} bpm).")
        if patient.systolic_bp > 140 or patient.diastolic_bp > 90:
            explanation.append("Blood pressure is elevated.")
        explanation.append(f"AI Confidence: {risk_proba:.2%} (Risk), {dept_proba:.2%} (Department)")

        # -----------------------------
        # Save to Supabase
        # -----------------------------
        try:
            supabase.table("triage_records").insert({
                "age": patient.age,
                "gender": patient.gender,
                "heart_rate": patient.heart_rate,
                "systolic_bp": patient.systolic_bp,
                "diastolic_bp": patient.diastolic_bp,
                "temperature": patient.temperature,
                "symptom": patient.symptom,
                "history": patient.history,
                "risk_level": risk_level,
                "department": department,
                "confidence": risk_proba,
                "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }).execute()

            logger.info("✅ Record saved to database.")

        except Exception as db_error:
            logger.error("❌ Database save failed: %s", db_error)

        # Return Response
        return {
            "risk_level": risk_level,
            "department": department,
            "explanation": explanation,
            "confidence_score": risk_proba,
            "risk_probabilities": risk_probs
        }

    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Fetch All Records (Doctor View)
# -----------------------------
@app.get("/api/records")
def get_all_records():
    try:
        response = supabase.table("triage_records") \
            .select("*") \
            .order("created_at", desc=True) \
            .execute()

        return response.data

    except Exception as e:
        logger.error("Fetching records failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Health Check
# -----------------------------
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

# -----------------------------
# Serve Frontend
# -----------------------------
app.mount("/", StaticFiles(directory="../client", html=True), name="static")


@app.post("/api/priority")
def priority_endpoint(patient: dict):
    score = calculate_priority(patient)
    level = get_priority_level(score)
    return {"score": score, "priority": level}


@app.post("/api/patient")
def add_patient(patient: dict):
    # 1️⃣ Calculate priority
    score = calculate_priority(patient)
    level = get_priority_level(score)

    # 2️⃣ Save to database
    response = supabase.table("patients").insert({
        "name": patient['name'],
        "risk_level": patient['risk_level'],
        "severity": patient['severity'],
        "days_sick": patient.get('days_sick', 0),
        "priority_score": score,
        "priority_level": level
    }).execute()

    return {"message": "Patient added", "priority_score": score, "priority_level": level}

@app.get("/api/patients")
def get_patients():
    # Fetch all patients sorted by priority_score descending (HIGH first)
    response = supabase.table("patients").select("*").order("priority_score", desc=True).execute()
    
    # Make sure response.data exists
    patients = response.data if response.data else []

    return {"patients": patients}