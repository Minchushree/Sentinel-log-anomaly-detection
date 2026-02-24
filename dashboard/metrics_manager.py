import json
from pathlib import Path
from datetime import datetime

METRICS_FILE = Path("dashboard/metrics.json")

def read_metrics():
    with open(METRICS_FILE, "r") as f:
        return json.load(f)

def write_metrics(data):
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def update_metrics(detection_result, correlations=None, correlation_engine=None, brute_force_data=None, attack_sequences=None):
    """
    Update metrics with detection result and correlation data
    detection_result: dict with is_anomaly, attack_pattern, severity_score
    correlations: dict with correlation findings
    correlation_engine: CorrelationEngine instance for risk scores
    brute_force_data: dict with brute force statistics
    attack_sequences: list of multi-stage attack sequences
    """
    data = read_metrics()

    data["total_logs"] += 1
    if detection_result.get("is_anomaly"):
        data["anomaly_count"] += 1

    # Track attack patterns
    if detection_result.get("attack_pattern"):
        attack_type = detection_result["attack_pattern"]["type"]
        if "attack_patterns" not in data:
            data["attack_patterns"] = {}
        if attack_type not in data["attack_patterns"]:
            data["attack_patterns"][attack_type] = 0
        data["attack_patterns"][attack_type] += 1

    # Track severity scores and distribution
    if "severity_history" not in data:
        data["severity_history"] = []
    severity_score = detection_result.get("severity_score", 0)
    data["severity_history"].append(severity_score)
    data["severity_history"] = data["severity_history"][-100:]  # Keep last 100
    
    # Update severity distribution
    if "severity_distribution" not in data:
        data["severity_distribution"] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    if severity_score >= 75:
        data["severity_distribution"]["critical"] += 1
    elif severity_score >= 50:
        data["severity_distribution"]["high"] += 1
    elif severity_score >= 25:
        data["severity_distribution"]["medium"] += 1
    else:
        data["severity_distribution"]["low"] += 1
    
    # Track correlations
    if "correlation_stats" not in data:
        data["correlation_stats"] = {
            "correlated_attacks": 0,
            "brute_force_attempts": 0,
            "targeted_endpoints": 0,
            "suspicious_ips": 0
        }
    
    if correlations:
        if correlations.get("same_ip_attacks"):
            data["correlation_stats"]["correlated_attacks"] += 1
        if correlations.get("rapid_sequence"):
            data["correlation_stats"]["brute_force_attempts"] += 1

    # Update brute force data
    if brute_force_data:
        if "brute_force_data" not in data:
            data["brute_force_data"] = {
                "total_events": 0,
                "unique_sources": 0,
                "avg_rate": 0
            }
        data["brute_force_data"].update(brute_force_data)

    # Track attack sequences
    if attack_sequences:
        if "attack_sequences" not in data:
            data["attack_sequences"] = []
        for seq in attack_sequences:
            if seq not in data["attack_sequences"]:
                data["attack_sequences"].append(seq)
        data["attack_sequences"] = data["attack_sequences"][-50:]  # Keep last 50

    # Update attack timeline
    if "attack_timeline" not in data:
        data["attack_timeline"] = []
    if detection_result.get("is_anomaly"):
        data["attack_timeline"].append(1)
    else:
        if len(data["attack_timeline"]) > 0:
            data["attack_timeline"].append(0)
    data["attack_timeline"] = data["attack_timeline"][-50:]

    # Update attack trend (cumulative)
    if "attack_trend" not in data:
        data["attack_trend"] = []
    cumulative = sum(data["attack_timeline"])
    data["attack_trend"] = [sum(data["attack_timeline"][:i+1]) for i in range(len(data["attack_timeline"]))]

    # Update high-risk entities
    if correlation_engine:
        if "high_risk_ips" not in data:
            data["high_risk_ips"] = []
        if "high_risk_endpoints" not in data:
            data["high_risk_endpoints"] = []
        
        data["high_risk_ips"] = correlation_engine.get_suspicious_ips(threshold=50)
        data["high_risk_endpoints"] = correlation_engine.get_targeted_endpoints(threshold=25)

    data["log_timeline"].append(data["total_logs"])
    data["anomaly_timeline"].append(data["anomaly_count"])

    # keep last 50 points only
    data["log_timeline"] = data["log_timeline"][-50:]
    data["anomaly_timeline"] = data["anomaly_timeline"][-50:]

    data["last_updated"] = datetime.now().isoformat()

    write_metrics(data)

