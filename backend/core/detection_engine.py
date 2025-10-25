"""
Multi-layered detection engine combining:
- Anomaly detection (PyOD)
- Rule-based detection (Sigma rules)
- TTP mapping (MITRE ATT&CK)
- Threat intelligence matching (offline IoC database)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from config import DATA_DIR
from functools import lru_cache
from services.ai_engine import AIEngine


class DetectionEngine:
    """Unified detection engine for Project Quorum"""
    
    def __init__(self):
        # Load AI engine
        self.ai_engine = AIEngine()
        
        # Load threat intelligence (offline)
        self.threat_intel = self._load_threat_intel()
        
        # Load detection rules (Sigma-like format)
        self.rules = self._load_rules()
        
        # MITRE ATT&CK TTP mapping
        self.ttp_patterns = self._load_ttp_patterns()
        self._tfidf_cache = {}  # Cache vectorized messages
    
    def _load_threat_intel(self) -> Dict[str, List[str]]:
        """Load offline threat intelligence database"""
        intel_file = DATA_DIR / "threat_intel" / "indicators.json"
        if not intel_file.exists():
            return {"ips": [], "domains": [], "hashes": [], "processes": []}
        
        with open(intel_file, 'r') as f:
            return json.load(f)
    
    def _load_rules(self) -> List[Dict]:
        """Load detection rules (simplified Sigma format)"""
        rules_dir = DATA_DIR / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        rules = []
        for rule_file in rules_dir.glob("*.json"):
            with open(rule_file, 'r') as f:
                rules.extend(json.load(f))
        
        return rules
    
    def _load_ttp_patterns(self) -> Dict[str, Dict]:
        """Load MITRE ATT&CK TTP detection patterns"""
        ttp_file = DATA_DIR / "mitre_attack" / "ttp_patterns.json"
        if not ttp_file.exists():
            return {}
        
        with open(ttp_file, 'r') as f:
            return json.load(f)
    
    def analyze_log(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive log analysis using all detection methods
        
        Returns:
        {
            'is_threat': bool,
            'severity': str,  # critical, high, medium, low
            'detections': [
                {
                    'type': 'anomaly|rule|ioc|ttp',
                    'name': str,
                    'score': float,
                    'details': dict
                }
            ]
        }
        """
        detections = []
        max_severity = 'low'
        
        # 1. Anomaly Detection (AI)
        anomaly_result = self._detect_anomaly(log_entry['message'])
        if anomaly_result['is_anomaly']:
            detections.append({
                'type': 'anomaly',
                'name': 'Statistical Anomaly',
                'score': anomaly_result['score'],
                'details': {'reason': 'Unusual pattern detected by ML model'}
            })
            max_severity = self._escalate_severity(max_severity, 'medium')
        
        # 2. Rule-Based Detection
        rule_matches = self._check_rules(log_entry)
        if rule_matches:
            detections.extend(rule_matches)
            for match in rule_matches:
                max_severity = self._escalate_severity(max_severity, match.get('severity', 'medium'))
        
        # 3. Threat Intelligence Matching
        ioc_matches = self._check_threat_intel(log_entry)
        if ioc_matches:
            detections.extend(ioc_matches)
            max_severity = self._escalate_severity(max_severity, 'high')
        
        # 4. TTP Detection (MITRE ATT&CK)
        ttp_matches = self._detect_ttps(log_entry)
        if ttp_matches:
            detections.extend(ttp_matches)
            for ttp in ttp_matches:
                max_severity = self._escalate_severity(max_severity, ttp.get('severity', 'high'))
        
        return {
            'is_threat': len(detections) > 0,
            'severity': max_severity,
            'detections': detections,
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_anomaly(self, message: str) -> Dict:
        """AI-based anomaly detection"""
        if not message or not isinstance(message, str):
            return {'is_anomaly': False, 'score': 0.0}

        analysis_result = self.ai_engine.analyze([message])
        
        is_anomaly = analysis_result['anomaly_count'] > 0
        score = 0.0
        if is_anomaly:
            score = analysis_result['anomalies'][0]['score']

        return {
            'is_anomaly': is_anomaly,
            'score': score
        }
    
    def _check_rules(self, log_entry: Dict) -> List[Dict]:
        """Rule-based detection (Sigma-like)"""
        matches = []
        
        for rule in self.rules:
            if self._rule_matches(rule, log_entry):
                matches.append({
                    'type': 'rule',
                    'name': rule['title'],
                    'score': 1.0,
                    'severity': rule.get('level', 'medium'),
                    'details': {
                        'rule_id': rule.get('id'),
                        'description': rule.get('description'),
                        'tags': rule.get('tags', [])
                    }
                })
        
        return matches
    
    def _rule_matches(self, rule: Dict, log_entry: Dict) -> bool:
        """Check if a rule matches a log entry"""
        detection = rule.get('detection', {})
        
        # Simple keyword matching (can be extended)
        keywords = detection.get('keywords', [])
        message = log_entry.get('message', '').lower()
        
        for keyword in keywords:
            if keyword.lower() in message:
                return True
        
        # Process name matching
        if 'process' in detection:
            if log_entry.get('process') == detection['process']:
                return True
        
        return False
    
    def _check_threat_intel(self, log_entry: Dict) -> List[Dict]:
        """Match against offline threat intelligence"""
        matches = []
        message = log_entry.get('message', '')
        
        # IP address matching
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips_in_log = re.findall(ip_pattern, message)
        
        for ip in ips_in_log:
            if ip in self.threat_intel.get('ips', []):
                matches.append({
                    'type': 'ioc',
                    'name': 'Malicious IP Detected',
                    'score': 1.0,
                    'severity': 'high',
                    'details': {
                        'indicator': ip,
                        'indicator_type': 'ip_address'
                    }
                })
        
        # Domain matching
        domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'
        domains_in_log = re.findall(domain_pattern, message.lower())
        
        for domain in domains_in_log:
            if domain in self.threat_intel.get('domains', []):
                matches.append({
                    'type': 'ioc',
                    'name': 'Malicious Domain Detected',
                    'score': 1.0,
                    'severity': 'high',
                    'details': {
                        'indicator': domain,
                        'indicator_type': 'domain'
                    }
                })
        
        # Malicious process detection
        process = log_entry.get('process', '')
        if process in self.threat_intel.get('processes', []):
            matches.append({
                'type': 'ioc',
                'name': 'Malicious Process Detected',
                'score': 1.0,
                'severity': 'critical',
                'details': {
                    'indicator': process,
                    'indicator_type': 'process_name'
                }
            })
        
        return matches
    
    def _detect_ttps(self, log_entry: Dict) -> List[Dict]:
        """Detect MITRE ATT&CK TTPs"""
        matches = []
        message = log_entry.get('message', '').lower()
        
        for ttp_id, ttp_data in self.ttp_patterns.items():
            for pattern in ttp_data.get('patterns', []):
                if re.search(pattern, message, re.IGNORECASE):
                    matches.append({
                        'type': 'ttp',
                        'name': ttp_data['name'],
                        'score': 1.0,
                        'severity': ttp_data.get('severity', 'high'),
                        'details': {
                            'ttp_id': ttp_id,
                            'tactic': ttp_data.get('tactic'),
                            'technique': ttp_data.get('technique'),
                            'description': ttp_data.get('description')
                        }
                    })
                    break  # Only match once per TTP
        
        return matches
    
    def _escalate_severity(self, current: str, new: str) -> str:
        """Escalate severity level"""
        severity_order = ['low', 'medium', 'high', 'critical']
        
        current_idx = severity_order.index(current)
        new_idx = severity_order.index(new)
        
        return severity_order[max(current_idx, new_idx)]

    @lru_cache(maxsize=1000)
    def _cached_rule_match(self, message: str) -> tuple:
        """Cache rule matches for identical messages"""
        matches = []
        for rule in self.rules:
            if self._rule_matches(rule, {'message': message}):
                matches.append(rule['id'])
        return tuple(matches)
    
    def batch_analyze(self, log_entries: List[Dict]) -> List[Dict]:
        """Analyze multiple log entries efficiently"""
        results = []
        
        for entry in log_entries:
            result = self.analyze_log(entry)
            result['log_entry'] = entry
            results.append(result)
        
        return results
