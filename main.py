from sentinel.log_ingestor import follow
from sentinel.log_parser import parse_log
from sentinel.feature_extractor import extract_features
from sentinel.detector import detect_with_patterns
from sentinel.slack_alert import send_alert
from dashboard.metrics_manager import update_metrics

LOG_PATH = "data/access.log"

def process_line(line, alert_enabled=True):
    parsed = parse_log(line)
    if not parsed:
        return

    features = extract_features(parsed)
    detection_result = detect_with_patterns(features, parsed)
    
    # Update metrics
    update_metrics(detection_result)

    if detection_result["is_anomaly"] and alert_enabled:
        alert_msg = f"🚨 Alert: Suspicious activity detected\n{line.strip()}"
        
        # Add attack type if detected
        if detection_result["attack_pattern"]:
            alert_msg += f"\nType: {detection_result['attack_pattern']['type'].upper()}"
        
        send_alert(alert_msg)

print("📂 Processing existing logs...")
with open(LOG_PATH, "r") as f:
    for line in f:
        process_line(line, alert_enabled=False)

print("🛡️ Sentinel is monitoring logs in real time...")
log_file = open(LOG_PATH, "r")

for line in follow(log_file):
    process_line(line)

