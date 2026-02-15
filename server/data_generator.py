import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()

def generate_patient_data(num_samples=1000):
    data = []
    
    # Define possible values
    symptoms_list = [
        'Fever', 'Cough', 'Chest Pain', 'Shortness of Breath', 'Headache', 
        'Abdominal Pain', 'Dizziness', 'Nausea', 'Fatigue', 'Sore Throat',
        'Back Pain', 'Rash', 'Joint Pain', 'Vision Problems'
    ]
    
    conditions_list = [
        'None', 'Hypertension', 'Diabetes', 'Asthma', 'Heart Disease', 
        'Obesity', 'High Cholesterol', 'Arthritis', 'Migraine'
    ]

    for _ in range(num_samples):
        age = random.randint(1, 90)
        gender = random.choice(['Male', 'Female'])
        
        # Simulate vitals based on age/randomness (simplified)
        heart_rate = random.randint(60, 120)
        systolic_bp = random.randint(90, 160)
        diastolic_bp = random.randint(60, 100)
        temperature = round(random.uniform(36.0, 40.0), 1)
        
        symptom = random.choice(symptoms_list)
        history = random.choice(conditions_list)
        
        # Simple rule-based logic to assign Ground Truth for training
        # This acts as our "Expert Doctor" labeling the data
        risk_level = 'Low'
        department = 'General Medicine'
        
        # High Risk Rules
        if (temperature > 39.5) or (heart_rate > 110) or (systolic_bp > 150) or (symptom == 'Chest Pain') or (symptom == 'Shortness of Breath'):
            risk_level = 'High'
            if symptom == 'Chest Pain':
                department = 'Cardiology'
            elif symptom == 'Shortness of Breath':
                department = 'Emergency'
            else:
                department = 'Emergency'
        
        # Medium Risk Rules
        elif (temperature > 38.0) or (pain_scale := random.randint(1, 10)) > 6:
            risk_level = 'Medium'
            if symptom == 'Headache' or symptom == 'Dizziness':
                department = 'Neurology'
            elif symptom == 'Abdominal Pain':
                department = 'Gastroenterology' # Or General
            else:
                department = 'General Medicine'
                
        # Specific Department mapping for other symptoms
        if department == 'General Medicine':
            if symptom == 'Vision Problems':
                department = 'Ophthalmology'
            elif symptom == 'Joint Pain':
                department = 'Orthopedics'
            elif symptom == 'Rash':
                department = 'Dermatology'

        data.append({
            'Age': age,
            'Gender': gender,
            'Heart Rate': heart_rate,
            'Systolic BP': systolic_bp,
            'Diastolic BP': diastolic_bp,
            'Temperature': temperature,
            'Symptom': symptom,
            'History': history,
            'Risk Level': risk_level,
            'Department': department
        })
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_patient_data(5000)
    df.to_csv("patient_data.csv", index=False)
    print("Generated 5000 patient records to 'patient_data.csv'")
