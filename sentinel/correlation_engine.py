from datetime import datetime, timedelta
from collections import defaultdict

class CorrelationEngine:
    def __init__(self, time_window_minutes=5):
        """
        Initializes correlation engine with sliding time window.
        time_window_minutes: Period for grouping related anomalies
        """
        self.time_window_minutes = time_window_minutes
        self.anomaly_history = []
        self.correlations = []
        self.ip_attack_count = defaultdict(int)
        self.endpoint_attack_count = defaultdict(int)
    
    def record_anomaly(self, parsed_log, anomaly_info=None, attack_pattern=None):
        """Record an anomaly for correlation analysis"""
        record = {
            "timestamp": datetime.now(),
            "ip": parsed_log["ip"],
            "endpoint": parsed_log["endpoint"],
            "method": parsed_log["method"],
            "status": parsed_log["status"],
            "is_anomaly": bool(anomaly_info or attack_pattern),
            "attack_type": attack_pattern["type"] if attack_pattern else None,
            "severity": attack_pattern["severity"] if attack_pattern else None
        }
        
        self.anomaly_history.append(record)
        
        # Track attack counts per IP and endpoint
        if record["is_anomaly"]:
            self.ip_attack_count[record["ip"]] += 1
            self.endpoint_attack_count[record["endpoint"]] += 1
        
        # Keep only last 1000 records to avoid memory issues
        if len(self.anomaly_history) > 1000:
            self.anomaly_history.pop(0)
        
        return record
    
    def find_correlations(self, current_log):
        """Find related anomalies within time window"""
        now = datetime.now()
        time_threshold = now - timedelta(minutes=self.time_window_minutes)
        
        correlations = {
            "same_ip_attacks": [],
            "same_endpoint_attacks": [],
            "rapid_sequence": [],
            "attack_pattern_sequence": []
        }
        
        # Find attacks from same IP within time window
        same_ip = [
            r for r in self.anomaly_history 
            if r["ip"] == current_log["ip"] 
            and r["timestamp"] >= time_threshold 
            and r["is_anomaly"]
        ]
        if len(same_ip) > 1:
            correlations["same_ip_attacks"] = same_ip
        
        # Find attacks on same endpoint within time window
        same_endpoint = [
            r for r in self.anomaly_history 
            if r["endpoint"] == current_log["endpoint"] 
            and r["timestamp"] >= time_threshold 
            and r["is_anomaly"]
        ]
        if len(same_endpoint) > 1:
            correlations["same_endpoint_attacks"] = same_endpoint
        
        # Detect rapid sequence (potential brute force)
        rapid_window = now - timedelta(minutes=1)
        rapid_from_ip = [
            r for r in self.anomaly_history 
            if r["ip"] == current_log["ip"] 
            and r["timestamp"] >= rapid_window
        ]
        if len(rapid_from_ip) >= 5:  # 5+ requests in 1 minute
            correlations["rapid_sequence"] = rapid_from_ip
        
        # Detect attack pattern sequences
        attack_types_recent = [
            r for r in self.anomaly_history 
            if r["ip"] == current_log["ip"] 
            and r["timestamp"] >= time_threshold 
            and r["attack_type"]
        ]
        if len(attack_types_recent) > 1:
            correlations["attack_pattern_sequence"] = attack_types_recent
        
        return correlations
    
    def get_ip_risk_score(self, ip):
        """Calculate risk score for an IP based on attack history"""
        count = self.ip_attack_count[ip]
        
        # Risk escalates exponentially
        if count >= 10:
            return 100  # Critical
        elif count >= 5:
            return 75   # High
        elif count >= 3:
            return 50   # Medium
        elif count >= 1:
            return 25   # Low
        
        return 0
    
    def get_endpoint_risk_score(self, endpoint):
        """Calculate risk score for an endpoint based on attack history"""
        count = self.endpoint_attack_count[endpoint]
        
        if count >= 10:
            return 100
        elif count >= 5:
            return 75
        elif count >= 3:
            return 50
        elif count >= 1:
            return 25
        
        return 0
    
    def get_suspicious_ips(self, threshold=50):
        """Get list of IPs with risk score above threshold"""
        return [
            {"ip": ip, "risk_score": self.get_ip_risk_score(ip), "attack_count": count}
            for ip, count in self.ip_attack_count.items()
            if self.get_ip_risk_score(ip) >= threshold
        ]
    
    def get_targeted_endpoints(self, threshold=50):
        """Get list of endpoints being heavily targeted"""
        return [
            {"endpoint": ep, "risk_score": self.get_endpoint_risk_score(ep), "attack_count": count}
            for ep, count in self.endpoint_attack_count.items()
            if self.get_endpoint_risk_score(ep) >= threshold
        ]
    
    def reset(self):
        """Clear all correlation data"""
        self.anomaly_history.clear()
        self.ip_attack_count.clear()
        self.endpoint_attack_count.clear()
