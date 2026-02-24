import joblib
from sentinel.attack_patterns import detect_attack_pattern, get_attack_severity_score

model = joblib.load("model/anomaly_model.pkl")

def is_anomaly(features, parsed_log):
    # ML prediction
    ml_pred = model.predict(features)[0] == -1

    # Rule-based detection (GUARANTEED)
    rule_pred = False

    if parsed_log["status"] >= 500:
        rule_pred = True
    if parsed_log["status"] == 401:
        rule_pred = True
    if "admin" in parsed_log["endpoint"].lower():
        rule_pred = True
    if "'" in parsed_log["endpoint"] or "--" in parsed_log["endpoint"]:
        rule_pred = True

    return ml_pred or rule_pred

def detect_with_patterns(features, parsed_log):
    """Enhanced detection with attack pattern recognition"""
    is_anom = is_anomaly(features, parsed_log)
    attack_pattern = detect_attack_pattern(parsed_log["endpoint"], parsed_log["method"])
    
    return {
        "is_anomaly": is_anom or bool(attack_pattern),
        "attack_pattern": attack_pattern,
        "severity_score": get_attack_severity_score(attack_pattern) if attack_pattern else (50 if is_anom else 0)
    }
