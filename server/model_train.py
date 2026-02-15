import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

def train_model():
    # Load Data
    if not os.path.exists("patient_data.csv"):
        print("Data file not found. Please run data_generator.py first.")
        return

    df = pd.read_csv("patient_data.csv")
    
    # Preprocessing
    # Encoders for categorical data
    le_gender = LabelEncoder()
    le_symptom = LabelEncoder()
    le_history = LabelEncoder()
    le_risk = LabelEncoder()
    le_dept = LabelEncoder()
    
    df['Gender_Encoded'] = le_gender.fit_transform(df['Gender'])
    df['Symptom_Encoded'] = le_symptom.fit_transform(df['Symptom'])
    df['History_Encoded'] = le_history.fit_transform(df['History'])
    
    # Targets
    y_risk = le_risk.fit_transform(df['Risk Level'])
    y_dept = le_dept.fit_transform(df['Department'])
    
    # Features
    X = df[['Age', 'Gender_Encoded', 'Heart Rate', 'Systolic BP', 'Diastolic BP', 'Temperature', 'Symptom_Encoded', 'History_Encoded']]
    
    # Split Data
    X_train, X_test, y_risk_train, y_risk_test, y_dept_train, y_dept_test = train_test_split(
        X, y_risk, y_dept, test_size=0.2, random_state=42
    )
    
    # Train Models
    print("Training Risk Model...")
    risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
    risk_model.fit(X_train, y_risk_train)
    
    print("Training Department Model...")
    dept_model = RandomForestClassifier(n_estimators=100, random_state=42)
    dept_model.fit(X_train, y_dept_train)
    
    # Evaluate
    risk_preds = risk_model.predict(X_test)
    dept_preds = dept_model.predict(X_test)
    
    print("\nRisk Model Performance:")
    print(classification_report(y_risk_test, risk_preds, target_names=le_risk.classes_))
    
    print("\nDepartment Model Performance:")
    print(classification_report(y_dept_test, dept_preds, target_names=le_dept.classes_))
    
    # Save Artifacts
    artifacts = {
        'risk_model': risk_model,
        'dept_model': dept_model,
        'le_gender': le_gender,
        'le_symptom': le_symptom,
        'le_history': le_history,
        'le_risk': le_risk,
        'le_dept': le_dept
    }
    
    joblib.dump(artifacts, "triage_model.joblib")
    print("\nModel and encoders saved to 'triage_model.joblib'")

if __name__ == "__main__":
    train_model()
