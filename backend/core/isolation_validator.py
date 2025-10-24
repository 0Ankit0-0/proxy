import socket
import requests
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class IsolationValidator:
    """
    Validates that the system is truly isolated/air-gapped
    Detects potential security issues in deployment
    """
    
    @staticmethod
    def check_internet_connectivity() -> Tuple[bool, str]:
        """
        Check if system has internet access
        Returns: (has_internet, message)
        """
        test_hosts = [
            ("8.8.8.8", 53),      # Google DNS
            ("1.1.1.1", 53),      # Cloudflare DNS
        ]
        
        for host, port in test_hosts:
            try:
                socket.create_connection((host, port), timeout=2)
                return True, f"Internet detected: Can reach {host}:{port}"
            except (socket.timeout, socket.error):
                continue
        
        return False, "No internet connectivity detected"
    
    @staticmethod
    def check_external_api_access() -> List[str]:
        """
        Check if common external APIs are accessible
        Returns list of accessible endpoints (should be empty for isolation)
        """
        test_apis = [
            "https://api.github.com",
            "https://pypi.org",
            "https://www.google.com",
        ]
        
        accessible = []
        for api in test_apis:
            try:
                response = requests.get(api, timeout=2)
                if response.status_code < 500:
                    accessible.append(api)
            except requests.exceptions.RequestException:
                continue
        
        return accessible
    
    @staticmethod
    def check_network_interfaces() -> Dict[str, List[str]]:
        """
        List all active network interfaces
        For true isolation, should only have loopback
        """
        import psutil
        
        interfaces = {}
        for interface, addrs in psutil.net_if_addrs().items():
            ip_list = []
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_list.append(addr.address)
            
            if ip_list:
                interfaces[interface] = ip_list
        
        return interfaces
    
    @staticmethod
    def validate_isolation() -> Dict:
        """
        Comprehensive isolation validation
        Returns validation report
        """
        report = {
            "isolation_level": "unknown",
            "warnings": [],
            "info": {},
            "compliant": True
        }
        
        # Check 1: Internet connectivity
        has_internet, internet_msg = IsolationValidator.check_internet_connectivity()
        report["info"]["internet_check"] = internet_msg
        
        if has_internet:
            report["warnings"].append("⚠️ Internet connectivity detected - not fully air-gapped")
            report["isolation_level"] = "lan_connected"
            report["compliant"] = False
        
        # Check 2: Network interfaces
        interfaces = IsolationValidator.check_network_interfaces()
        report["info"]["network_interfaces"] = interfaces
        
        non_loopback = {k: v for k, v in interfaces.items() 
                       if not any(ip.startswith("127.") for ip in v)}
        
        if non_loopback:
            report["warnings"].append(
                f"⚠️ Non-loopback interfaces active: {list(non_loopback.keys())}"
            )
            if not has_internet:
                report["isolation_level"] = "lan_isolated"
        else:
            report["isolation_level"] = "fully_isolated"
        
        # Check 3: External API access (if internet available)
        if has_internet:
            accessible_apis = IsolationValidator.check_external_api_access()
            if accessible_apis:
                report["warnings"].append(
                    f"⚠️ Can access external APIs: {accessible_apis}"
                )
        
        # Summary
        if not report["warnings"]:
            report["compliant"] = True
            report["isolation_level"] = "fully_isolated"
        
        return report
