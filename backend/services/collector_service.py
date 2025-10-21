import os
import shutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime as dt
from config import LOGS_DIR, TEMP_DIR
from typing import List, Tuple, Optional
import paramiko
import winrm

LOGS_DIR = Path(LOGS_DIR)
TEMP_DIR = Path(TEMP_DIR)

class LogCollector:
    """
    Handle offline log collection from multiple OS & air-gapped environments
    Supports local collection and remote collection via SSH/WinRM
    """

    def __init__(self, logs_dir: Path = None, temp_dir: str = None):
        self.logs_dir = logs_dir if logs_dir else LOGS_DIR
        self.temp_dir = temp_dir if temp_dir else TEMP_DIR
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.supported_ext = [".log", ".txt", ".evtx", ".json", ".csv", ".evt", ".gz"]

    def collect_local(self) -> List[Path]:
        """Scan LOGS_DIR and return list of raw log file paths.
        Also copy matched files into a timestamped temp folder for processing."""

        collected = []
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.temp_dir / f"collected_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        for root, _, files in os.walk(self.logs_dir):
            for f in files:
                p = Path(root) / f
                if p.suffix.lower() in self.supported_ext or True:
                    try:
                        dst = dest / f
                        shutil.copy2(p, dst)
                        collected.append(dst)
                        print(f"[collected] Copied {p} to {dst}")
                    except Exception as e:
                        print(f"[collected] Error copying file {p}: {e}")
        return collected

    def collect_windows_logs(self) -> List[Path]:
        """Collect Windows Event Logs using wevtutil (local only)"""
        collected = []
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.temp_dir / f"windows_logs_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        if platform.system() != "Windows":
            print("[collected] Windows log collection only available on Windows systems")
            return collected

        # Common Windows Event Log channels
        channels = [
            "System", "Application", "Security",
            "Setup", "ForwardedEvents"
        ]

        for channel in channels:
            try:
                output_file = dest / f"{channel}.evtx"
                # Export using wevtutil
                cmd = f'wevtutil epl "{channel}" "{output_file}" /ow:true'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    collected.append(output_file)
                    print(f"[collected] Exported Windows {channel} log to {output_file}")
                else:
                    print(f"[collected] Failed to export {channel} log: {result.stderr}")

            except Exception as e:
                print(f"[collected] Error collecting Windows {channel} log: {e}")

        return collected

    def collect_network_logs(self, network_path: str, username: str = None, password: str = None) -> List[Path]:
        """Collect logs from network share (SMB/CIFS)"""
        collected = []
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.temp_dir / f"network_logs_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        try:
            # Mount network drive (Windows)
            if platform.system() == "Windows":
                drive_letter = "Z:"  # Use available drive letter
                if username and password:
                    cmd = f'net use {drive_letter} "{network_path}" /user:{username} {password} /persistent:no'
                else:
                    cmd = f'net use {drive_letter} "{network_path}" /persistent:no'

                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"[collected] Failed to mount network drive: {result.stderr}")
                    return collected

                # Copy files from mounted drive
                network_dir = Path(drive_letter)
                for root, _, files in os.walk(network_dir):
                    for f in files:
                        p = Path(root) / f
                        if p.suffix.lower() in self.supported_ext:
                            try:
                                dst = dest / f
                                shutil.copy2(p, dst)
                                collected.append(dst)
                                print(f"[collected] Copied network file {p} to {dst}")
                            except Exception as e:
                                print(f"[collected] Error copying network file {p}: {e}")

                # Unmount drive
                subprocess.run(f'net use {drive_letter} /delete /y', shell=True, capture_output=True)

            else:
                print("[collected] Network log collection currently only supported on Windows")

        except Exception as e:
            print(f"[collected] Error in network log collection: {e}")

        return collected

    def collect_remote_ssh(self, host: str, username: str, key_path: str = None,
                          password: str = None, remote_paths: List[str] = None) -> List[Path]:
        """Collect logs from remote Linux/Unix systems via SSH"""
        collected = []
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.temp_dir / f"remote_ssh_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect using key or password
            if key_path:
                private_key = paramiko.RSAKey.from_private_key_file(key_path)
                ssh.connect(host, username=username, pkey=private_key)
            elif password:
                ssh.connect(host, username=username, password=password)
            else:
                raise ValueError("Either key_path or password must be provided")

            # Open SFTP session
            sftp = ssh.open_sftp()

            # Download files
            for remote_path in remote_paths or ["/var/log/syslog", "/var/log/auth.log"]:
                try:
                    remote_file = Path(remote_path)
                    local_file = dest / remote_file.name

                    sftp.get(str(remote_file), str(local_file))
                    collected.append(local_file)
                    print(f"[collected] Downloaded {remote_path} to {local_file}")

                except Exception as e:
                    print(f"[collected] Error downloading {remote_path}: {e}")

            sftp.close()
            ssh.close()

        except Exception as e:
            print(f"[collected] SSH collection error: {e}")

        return collected

    def collect_remote_winrm(self, host: str, username: str, password: str,
                           remote_paths: List[str] = None) -> List[Path]:
        """Collect logs from remote Windows systems via WinRM"""
        collected = []
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.temp_dir / f"remote_winrm_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize WinRM session
            session = winrm.Session(f'http://{host}:5985/wsman',
                                  auth=(username, password),
                                  transport='ntlm')

            # Default Windows log paths
            default_paths = [
                'C:\\Windows\\System32\\winevt\\Logs\\System.evtx',
                'C:\\Windows\\System32\\winevt\\Logs\\Application.evtx',
                'C:\\Windows\\System32\\winevt\\Logs\\Security.evtx'
            ]

            for remote_path in remote_paths or default_paths:
                try:
                    # Use PowerShell to copy file to temp location and read it
                    ps_script = f'''
                    $tempFile = [System.IO.Path]::GetTempFileName()
                    Copy-Item "{remote_path}" $tempFile
                    [Convert]::ToBase64String([IO.File]::ReadAllBytes($tempFile))
                    Remove-Item $tempFile
                    '''

                    result = session.run_ps(ps_script)

                    if result.status_code == 0:
                        # Decode base64 content
                        import base64
                        file_content = base64.b64decode(result.std_out.decode())

                        local_file = dest / Path(remote_path).name
                        with open(local_file, 'wb') as f:
                            f.write(file_content)

                        collected.append(local_file)
                        print(f"[collected] Downloaded {remote_path} to {local_file}")
                    else:
                        print(f"[collected] Failed to download {remote_path}: {result.std_err.decode()}")

                except Exception as e:
                    print(f"[collected] Error downloading {remote_path}: {e}")

        except Exception as e:
            print(f"[collected] WinRM collection error: {e}")

        return collected

    def read_raw_file(self, file_path: Path, max_bytes: int = 10_000_000) -> Tuple[Path, bytes]:
        """
        Read raw file bytes (up to max_bytes). Useful for handing raw content to parser.
        Returns (path, content_bytes)
        """
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        with file_path.open("rb") as f:
            content = f.read(max_bytes)

        return (file_path, content)
