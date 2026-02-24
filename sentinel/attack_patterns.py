import re

# Known attack patterns and their severity levels
ATTACK_PATTERNS = {
    "sql_injection": {
        "severity": "critical",
        "patterns": [
            r"(?i)(union.*select|select.*from|insert.*into|delete.*from|drop.*table|update.*set)",
            r"(?i)(or\s+1\s*=\s*1|or\s+1\s*=\s*1--)",
            r"(?i)(';.*--|--.*|/\*.*\*/)",
            r"(?i)(sleep\s*\(\s*\d+|benchmark\s*\()",
        ],
        "description": "SQL Injection attempt detected"
    },
    "xss_attack": {
        "severity": "high",
        "patterns": [
            r"(?i)(<script|javascript:|onerror|onload|onclick|<iframe)",
            r"(?i)(<svg|<img.*on|eval\()",
        ],
        "description": "Cross-Site Scripting (XSS) attempt detected"
    },
    "brute_force": {
        "severity": "high",
        "description": "Brute force attack pattern detected",
        "patterns": []  # Handled separately by request frequency
    },
    "path_traversal": {
        "severity": "high",
        "patterns": [
            r"(\.\./|\.\.\\|%2e%2e|%252e)",
            r"(/etc/passwd|/proc/|c:\\windows|c:\\winnt)",
        ],
        "description": "Path traversal attempt detected"
    },
    "command_injection": {
        "severity": "critical",
        "patterns": [
            r"(?i)(;\s*(cat|ls|dir|wget|curl|nc|bash|cmd|powershell))",
            r"(?i)(\||&&|`|\\$\()",
        ],
        "description": "Command injection attempt detected"
    },
    "ldap_injection": {
        "severity": "high",
        "patterns": [
            r"(?i)(\*|\(|\)|&|\|)",  # LDAP special chars in unusual context
        ],
        "description": "LDAP injection attempt detected"
    },
    "xxe_attack": {
        "severity": "high",
        "patterns": [
            r"(?i)(<!DOCTYPE|<!ENTITY|SYSTEM|PUBLIC)",
        ],
        "description": "XML External Entity (XXE) attack detected"
    }
}

def detect_attack_pattern(endpoint, method="GET"):
    """
    Detect known attack patterns in endpoint.
    Returns: (pattern_type, severity, description) or None
    """
    for pattern_type, pattern_data in ATTACK_PATTERNS.items():
        if pattern_type == "brute_force":
            continue  # Handle separately
        
        for pattern in pattern_data["patterns"]:
            if re.search(pattern, endpoint):
                return {
                    "type": pattern_type,
                    "severity": pattern_data["severity"],
                    "description": pattern_data["description"]
                }
    
    return None

def get_attack_severity_score(attack_info):
    """Convert severity level to numeric score for ranking"""
    severity_scores = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }
    return severity_scores.get(attack_info["severity"], 0) if attack_info else 0
