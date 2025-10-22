import os
import shutil
import platform
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime as dt
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogCollector:
    """
    Comprehensive log collector for Windows, Linux, and macOS
    Supports local system log collection from OS-specific locations
    """

    def __init__(self, output_dir: Optional[Path] = None, logs_dir: Optional[Path] = None, temp_dir: Optional[Path] = None):
        # For backward compatibility, if output_dir is provided, use it
        # Otherwise, use temp_dir as output_dir
        if output_dir:
            self.output_dir = Path(output_dir)
        elif temp_dir:
            self.output_dir = Path(temp_dir)
        else:
            self.output_dir = Path(tempfile.gettempdir()) / "log_collection"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logs_dir = logs_dir or Path.cwd() / "logs"
        self.temp_dir = temp_dir or self.output_dir
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

    def collect_local(self) -> List[Path]:
        """Collect logs from local directory specified in logs_dir"""
        logger.info(f"📁 Collecting logs from {self.logs_dir}...")
        collected_files = []

        if not self.logs_dir.exists():
            logger.warning(f"⚠️ Logs directory {self.logs_dir} does not exist")
            return collected_files

        # Find all log files in the directory
        for file_path in self.logs_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.log', '.txt', '.json', '.csv']:
                dest_file = self.output_dir / file_path.name
                shutil.copy2(file_path, dest_file)
                collected_files.append(dest_file)
                self.collected_files.append(dest_file)
                logger.info(f"✅ Collected: {file_path.name}")

        return collected_files

    def collect_network_logs(self, network_path: str, username: str = None, password: str = None) -> List[Path]:
        """Collect logs from network share (Windows only)"""
        if self.system != "Windows":
            logger.warning("⚠️ Network log collection only supported on Windows")
            return []

        logger.info(f"🌐 Collecting logs from network share: {network_path}")
        collected_files = []

        try:
            # Mount network drive
            drive_letter = "Z:"  # Use Z: as temporary drive
            cmd_mount = f'net use {drive_letter} "{network_path}"'
            if username and password:
                cmd_mount += f' /user:{username} {password}'

            result_mount = subprocess.run(cmd_mount, shell=True, capture_output=True, text=True)
            if result_mount.returncode != 0:
                logger.error(f"❌ Failed to mount network drive: {result_mount.stderr}")
                return collected_files

            # Copy files from mounted drive
            network_dir = Path(drive_letter)
            for file_path in network_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.log', '.txt', '.evtx']:
                    dest_file = self.output_dir / file_path.name
                    shutil.copy2(file_path, dest_file)
                    collected_files.append(dest_file)
                    self.collected_files.append(dest_file)
                    logger.info(f"✅ Collected from network: {file_path.name}")

            # Unmount network drive
            cmd_unmount = f'net use {drive_letter} /delete'
            subprocess.run(cmd_unmount, shell=True, capture_output=True)

        except Exception as e:
            logger.error(f"❌ Error collecting network logs: {e}")

        return collected_files

    def collect_remote_ssh(self, host: str, username: str, password: str, remote_paths: List[str] = None) -> List[Path]:
        """Collect logs from remote server via SSH"""
        try:
            import paramiko
        except ImportError:
            logger.error("❌ paramiko not installed. Install with: pip install paramiko")
            return []

        logger.info(f"🔐 Collecting logs from {host} via SSH")
        collected_files = []

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=username, password=password)

            sftp = ssh.open_sftp()

            remote_paths = remote_paths or ["/var/log/syslog", "/var/log/messages"]

            for remote_path in remote_paths:
                try:
                    # Get file info
                    stat = sftp.stat(remote_path)
                    if stat.st_size > 50 * 1024 * 1024:  # Skip files larger than 50MB
                        logger.warning(f"⚠️ Skipping large file: {remote_path}")
                        continue

                    # Download file
                    local_filename = Path(remote_path).name
                    local_path = self.output_dir / f"ssh_{host}_{local_filename}"
                    sftp.get(remote_path, str(local_path))
                    collected_files.append(local_path)
                    self.collected_files.append(local_path)
                    logger.info(f"✅ Collected via SSH: {remote_path}")

                except Exception as e:
                    logger.warning(f"⚠️ Failed to collect {remote_path}: {e}")

            sftp.close()
            ssh.close()

        except Exception as e:
            logger.error(f"❌ SSH collection failed: {e}")

        return collected_files

    def collect_remote_winrm(self, host: str, username: str, password: str, remote_paths: List[str] = None) -> List[Path]:
        """Collect logs from remote Windows server via WinRM"""
        try:
            import winrm
        except ImportError:
            logger.error("❌ pywinrm not installed. Install with: pip install pywinrm")
            return []

        logger.info(f"🪟 Collecting logs from {host} via WinRM")
        collected_files = []

        try:
            session = winrm.Session(host, auth=(username, password))

            remote_paths = remote_paths or [
                "C:\\Windows\\System32\\winevt\\Logs\\System.evtx",
                "C:\\Windows\\System32\\winevt\\Logs\\Application.evtx",
                "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx"
            ]

            for remote_path in remote_paths:
                try:
                    # Use PowerShell to read and encode file content
                    ps_script = f"""
                    if (Test-Path "{remote_path}") {{
                        $content = Get-Content "{remote_path}" -Encoding Byte -TotalCount 1048576
                        [System.Convert]::ToBase64String($content)
                    }}
                    """

                    result = session.run_ps(ps_script)

                    if result.status_code == 0 and result.std_out:
                        # Decode base64 content
                        import base64
                        file_content = base64.b64decode(result.std_out.decode())

                        local_filename = Path(remote_path).name
                        local_path = self.output_dir / f"winrm_{host}_{local_filename}"
                        with open(local_path, 'wb') as f:
                            f.write(file_content)

                        collected_files.append(local_path)
                        self.collected_files.append(local_path)
                        logger.info(f"✅ Collected via WinRM: {remote_path}")
                    else:
                        logger.warning(f"⚠️ Failed to collect {remote_path}")

                except Exception as e:
                    logger.warning(f"⚠️ Error collecting {remote_path}: {e}")

        except Exception as e:
            logger.error(f"❌ WinRM collection failed: {e}")

        return collected_files

    def read_raw_file(self, file_path: Path, max_bytes: int = None) -> tuple[Path, bytes]:
        """Read raw file content with optional size limit"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'rb') as f:
            if max_bytes:
                content = f.read(max_bytes)
            else:
                content = f.read()

        return file_path, content

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
    collector = LogCollector(output_dir=Path("/tmp/collected_logs"))
    collected = collector.collect_all()

    print("\n📊 Collection Report:")
    report = collector.get_collection_report()
    for key, value in report.items():
        if key != "files":
            print(f"  {key}: {value}")

    print(f"\n✅ Collected {len(collected)} log files")
