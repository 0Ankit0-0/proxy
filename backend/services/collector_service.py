# import polars as pl
import os
import shutil

from pathlib import Path
from datetime import datetime as dt
from config import LOGS_DIR, TEMP_DIR
from typing import List, Tuple

LOGS_DIR = Path(LOGS_DIR)
TEMP_DIR = Path(TEMP_DIR)

class LogCollector:
    """
    Handle offline log collection from multiple OS & air-gapped environments
    """
    record = []
    def __init__(self, logs_dir: Path = None, temp_dir: str = None):
        self.logs_dir = logs_dir if logs_dir else LOGS_DIR
        self.temp_dir = temp_dir if temp_dir else TEMP_DIR
        self.temp_dir.mkdir(parents = True, exist_ok = True)
        # self.supported_os = ["windows", "linux", "macos"]
        self.supported_ext = [".log", ".txt", ".evtx", ".json", ".csv", ".evt", ".gz"]
    
    def collect_local(self) -> List[Path]:
        """Scan LOGS_DIR and return list of raw log file paths.
        Also copy matched files into a timestamped temp folder for processing."""
        
        collected = []
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        dest = self.temp_dir / f"collected_{timestamp}"
        dest.mkdir(parents = True, exist_ok = True)
        
        for root, _, files in os.walk(self.logs_dir):
            for f in files:
                p = Path(root) / f
                if p.suffix.lower() in self.supported_ext or True:
                    try:
                        dst = dest / f
                        shutil.copy2(p, dst)
                        collected.append(dst)
                    except Exception as e:
                        print(f"[collected] Error copying file {p}: {e}") 
        return collected

    def collect_remote(self, host: str, username: str, key_path: str = None, path_list: List[str] = None) -> List[Path]:
        """Placeholder for remote collection via SSH/WinRM.
        Implement using `paramiko` (SSH) for Linux/macOS and `pywinrm` for Windows.
        Returns list of downloaded file paths into temp_dir.

        Example pattern:
           - create ssh client
           - for each path in path_list: sftp.get(path, local_dest)"""
        pass
    
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
