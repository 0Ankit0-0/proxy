import os
import shutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime as dt
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossPlatformLogCollector:
    """
    Comprehensive log collector for Windows, Linux, and macOS
    Supports local system log collection from OS-specific locations
    """

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.system = platform.system()
        self.collected_files: List[Path] = []
        
        # Define log locations per OS
        self.log_paths = self._get_system_log_paths()

    def _get_system_log_paths(self) -> Dict[str, List[str]]:
        """Get OS-specific log file paths"""
        
        if self.system == "Linux":
            return {
                "system": [
                    "/var/log/syslog",
                    "/var/log/messages",
                    "/var/log/kern.log",
                    "/var/log/dmesg",
                ],
                "auth": [
                    "/var/log/auth.log",
                    "/var/log/secure",
                ],
                "application": [
                    "/var/log/apache2/*.log",
                    "/var/log/nginx/*.log",
                    "/var/log/mysql/*.log",
                ],
                "journal": ["journalctl"]  # Special handling
            }
        
        elif self.system == "Darwin":  # macOS
            return {
                "system": [
                    "/var/log/system.log",
                    "/var/log/install.log",
                ],
                "auth": [
                    "/var/log/secure.log",
                ],
                "application": [
                    "/Library/Logs/*.log",
                    "~/Library/Logs/*.log",
                ],
                "unified": ["log show"]  # macOS Unified Logging
            }
        
        elif self.system == "Windows":
            return {
                "event_logs": [
                    "System",
                    "Application",
                    "Security",
                    "Setup",
                ]
            }
        
        return {}

    def collect_linux_logs(self) -> List[Path]:
        """Collect logs from Linux systems"""
        logger.info("🐧 Collecting Linux logs...")
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.output_dir / f"linux_logs_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        # Collect standard log files
        for category, paths in self.log_paths.items():
            if category == "journal":
                # Handle systemd journal separately
                self._collect_journalctl(dest)
                continue
            
            for path_pattern in paths:
                try:
                    # Handle wildcards
                    from glob import glob
                    matching_files = glob(path_pattern)
                    
                    for log_file in matching_files:
                        log_path = Path(log_file)
                        if log_path.exists() and log_path.is_file():
                            dest_file = dest / f"{category}_{log_path.name}"
                            shutil.copy2(log_path, dest_file)
                            self.collected_files.append(dest_file)
                            logger.info(f"✅ Collected: {log_file}")
                except PermissionError:
                    logger.warning(f"⚠️ Permission denied: {path_pattern}")
                except Exception as e:
                    logger.error(f"❌ Error collecting {path_pattern}: {e}")

        return self.collected_files

    def _collect_journalctl(self, dest: Path):
        """Collect systemd journal logs"""
        try:
            output_file = dest / "journalctl.log"
            # Get last 10,000 lines
            cmd = ["journalctl", "-n", "10000", "--no-pager"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                self.collected_files.append(output_file)
                logger.info(f"✅ Collected journalctl logs")
            else:
                logger.warning(f"⚠️ journalctl failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("❌ journalctl command timed out")
        except FileNotFoundError:
            logger.warning("⚠️ journalctl not found (non-systemd system?)")
        except Exception as e:
            logger.error(f"❌ Error collecting journalctl: {e}")

    def collect_macos_logs(self) -> List[Path]:
        """Collect logs from macOS systems"""
        logger.info("🍎 Collecting macOS logs...")
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.output_dir / f"macos_logs_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        # Collect standard log files
        for category, paths in self.log_paths.items():
            if category == "unified":
                # Handle macOS Unified Logging
                self._collect_macos_unified(dest)
                continue
            
            for path_pattern in paths:
                try:
                    # Expand user directory
                    path_pattern = os.path.expanduser(path_pattern)
                    from glob import glob
                    matching_files = glob(path_pattern)
                    
                    for log_file in matching_files:
                        log_path = Path(log_file)
                        if log_path.exists() and log_path.is_file():
                            dest_file = dest / f"{category}_{log_path.name}"
                            shutil.copy2(log_path, dest_file)
                            self.collected_files.append(dest_file)
                            logger.info(f"✅ Collected: {log_file}")
                except PermissionError:
                    logger.warning(f"⚠️ Permission denied: {path_pattern}")
                except Exception as e:
                    logger.error(f"❌ Error collecting {path_pattern}: {e}")

        return self.collected_files

    def _collect_macos_unified(self, dest: Path):
        """Collect macOS Unified Logging System logs"""
        try:
            output_file = dest / "unified_log.txt"
            # Get last 1 hour of logs
            cmd = ["log", "show", "--predicate", "processImagePath contains 'System'", 
                   "--style", "syslog", "--last", "1h"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                self.collected_files.append(output_file)
                logger.info(f"✅ Collected unified logs")
            else:
                logger.warning(f"⚠️ log show failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("❌ log show command timed out")
        except Exception as e:
            logger.error(f"❌ Error collecting unified logs: {e}")

    def collect_windows_logs(self) -> List[Path]:
        """Collect Windows Event Logs using wevtutil"""
        logger.info("🪟 Collecting Windows logs...")
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.output_dir / f"windows_logs_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        for channel in self.log_paths.get("event_logs", []):
            try:
                output_file = dest / f"{channel}.evtx"
                cmd = f'wevtutil epl "{channel}" "{output_file}" /ow:true'
                result = subprocess.run(cmd, shell=True, capture_output=True, 
                                     text=True, timeout=30)

                if result.returncode == 0:
                    self.collected_files.append(output_file)
                    logger.info(f"✅ Collected Windows {channel} log")
                else:
                    logger.warning(f"⚠️ Failed to export {channel}: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Timeout collecting {channel}")
            except Exception as e:
                logger.error(f"❌ Error collecting {channel}: {e}")

        return self.collected_files

    def collect_all(self) -> List[Path]:
        """
        Main entry point: Detect OS and collect appropriate logs
        """
        logger.info(f"🚀 Starting log collection on {self.system}...")
        
        if self.system == "Linux":
            return self.collect_linux_logs()
        elif self.system == "Darwin":
            return self.collect_macos_logs()
        elif self.system == "Windows":
            return self.collect_windows_logs()
        else:
            logger.error(f"❌ Unsupported operating system: {self.system}")
            return []

    def get_collection_report(self) -> Dict:
        """Generate a summary report of collected logs"""
        total_size = sum(f.stat().st_size for f in self.collected_files if f.exists())
        
        return {
            "system": self.system,
            "timestamp": dt.now().isoformat(),
            "files_collected": len(self.collected_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files": [str(f) for f in self.collected_files]
        }


# Example usage
if __name__ == "__main__":
    collector = CrossPlatformLogCollector(output_dir=Path("/tmp/collected_logs"))
    collected = collector.collect_all()
    
    print("\n📊 Collection Report:")
    report = collector.get_collection_report()
    for key, value in report.items():
        if key != "files":
            print(f"  {key}: {value}")
    
    print(f"\n✅ Collected {len(collected)} log files")