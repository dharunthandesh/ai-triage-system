# -----------------------------
# Priority Calculation Functions
# -----------------------------
def calculate_priority(patient):
    score = 0

    # Risk level
    if patient['risk_level'] == "High":
        score += 50
    elif patient['risk_level'] == "Medium":
        score += 30
    else:
        score += 10

    # Symptom severity
    if patient['severity'] == "Severe":
        score += 20
    elif patient['severity'] == "Moderate":
        score += 10
    else:
        score += 5

    # Days sick (max 10 points)
    score += min(patient.get('days_sick', 0) * 2, 10)

    # Critical symptoms
    if patient.get('critical_symptoms', False):
        score += 15

    # Chronic conditions
    score += patient.get('chronic_conditions_count', 0) * 3

    return score


def get_priority_level(score):
    """Return priority level based on score"""
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"
