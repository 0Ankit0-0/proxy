import polars as pl
import re
from pathlib import Path
from typing import List, Optional
import datetime as dt
import json
import pandas as pd

SYSLOG_REGEX = re.compile(
    r'^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<proc>\S+?)(?:[[](?P<pid>\d+)]])?:\s+(?P<msg>.*)$'
)

RFC5424_REGEX = re.compile(
    r'<(?P<prio>\d{1,3})>(?P<ver>\d{1,2})? (?P<timestamp>\S+) (?P<hostname>\S+) (?P<app_name>\S+) (?P<proc_id>\S+) (?P<msg_id>\S+) (?P<structured_data>-|\[.*\]) (?P<msg>.*)'
)

MONTH_MAP = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}


class LogParser:
    """
    Parser Service - transform raw log lines/files to structured Polars DataFrames.
    """

    @staticmethod
    def _make_timestamp_from_syslog(month: str, day: str, time: str) -> Optional[dt.datetime]:
        try:
            now = dt.datetime.now()
            month_num = MONTH_MAP.get(month, now.month)

            return dt.datetime(
                year=now.year,
                month=month_num,
                day=int(day),
                hour=int(time.split(':')[0]),
                minute=int(time.split(':')[1]),
                second=int(time.split(':')[2])
            )
        except Exception:
            return None

    @staticmethod
    def parse_syslog_lines(lines: List[str]) -> pl.DataFrame:
        records = []
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue

            rec = None
            bsd_match = SYSLOG_REGEX.match(ln)
            rfc_match = RFC5424_REGEX.match(ln)

            if bsd_match:
                ts = LogParser._make_timestamp_from_syslog(bsd_match.group('month'), bsd_match.group('day'), bsd_match.group('time'))
                rec = {
                    "timestamp": ts,
                    "host": bsd_match.group("host"),
                    "process": bsd_match.group("proc"),
                    "pid": int(bsd_match.group("pid")) if bsd_match.group("pid") else None,
                    "message": bsd_match.group("msg"),
                    "raw": ln
                }
            elif rfc_match:
                try:
                    ts = pd.to_datetime(rfc_match.group('timestamp'))
                except:
                    ts = None
                rec = {
                    "timestamp": ts,
                    "host": rfc_match.group("hostname"),
                    "process": rfc_match.group("app_name"),
                    "pid": rfc_match.group("proc_id"),
                    "message": rfc_match.group("msg"),
                    "raw": ln
                }
            else:
                rec = {
                    "timestamp": None, "host": None, "process": None,
                    "pid": None, "message": ln, "raw": ln
                }
            records.append(rec)

        df = pl.DataFrame(records).with_columns([
            pl.col("timestamp").cast(pl.Datetime(time_unit = "ms")),
            pl.col("host").cast(pl.Utf8),
            pl.col("process").cast(pl.Utf8),
            pl.col("pid").cast(pl.Int64),
            pl.col("message").cast(pl.Utf8),
            pl.col("raw").cast(pl.Utf8),
        ])
        return df

    @staticmethod
    def parse_generic_text(lines: List[str]) -> pl.DataFrame:
        iso_ts_re = re.compile(r'(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})')
        records  = []

        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue

            m = iso_ts_re.search(ln)
            ts = None
            if m:
                try:
                    ts = dt.datetime.fromisoformat(m.group('ts'))
                except ValueError:
                    ts = None
            records.append({
                "timestamp": ts, "host": None, "process": None,
                "pid": None, "message": ln, "raw": ln
            })

        df = pl.DataFrame(records).with_columns([
            pl.col("timestamp").cast(pl.Datetime(time_unit = "ms")),
            pl.col("host").cast(pl.Utf8),
            pl.col("process").cast(pl.Utf8),
            pl.col("pid").cast(pl.Int64),
            pl.col("message").cast(pl.Utf8),
            pl.col("raw").cast(pl.Utf8),
        ])
        return df

    @staticmethod
    def parse_json_logs(lines: List[str]) -> pl.DataFrame:
        records = []
        for line in lines:
            try:
                log = json.loads(line)
                records.append({
                    "timestamp": pd.to_datetime(log.get("timestamp")),
                    "host": log.get("host", "unknown"),
                    "process": log.get("process", "unknown"),
                    "pid": None,
                    "message": log.get("message", line),
                    "raw": line
                })
            except json.JSONDecodeError:
                continue

        df = pl.DataFrame(records).with_columns([
            pl.col("timestamp").cast(pl.Datetime(time_unit = "ms")),
            pl.col("host").cast(pl.Utf8),
            pl.col("process").cast(pl.Utf8),
            pl.col("pid").cast(pl.Int64),
            pl.col("message").cast(pl.Utf8),
            pl.col("raw").cast(pl.Utf8),
        ])
        return df

    @staticmethod
    def parse_evtx_logs(file_path: Path) -> pl.DataFrame:
        try:
            import Evtx.Evtx as evtx
            import xml.etree.ElementTree as ET
        except ImportError:
            raise ImportError("python-evtx not installed: pip install python-evtx")
        
        records = []
        with evtx.Evtx(str(file_path)) as log:
            for record in log.records():
                try:
                    xml = record.xml()
                    root = ET.fromstring(xml)
                    ns = {'evt': 'http://schemas.microsoft.com/win/2004/08/events/event'}
                    system = root.find('.//evt:System', ns)
                    timestamp = system.find('.//evt:TimeCreated', ns).get('SystemTime')
                    event_id = system.find('.//evt:EventID', ns).text
                    computer = system.find('.//evt:Computer', ns).text
                    event_data = root.find('.//evt:EventData', ns)
                    message = ET.tostring(event_data, encoding='unicode') if event_data is not None else ""
                    
                    records.append({
                        'timestamp': pd.to_datetime(timestamp), 'host': computer,
                        'process': f'EventID_{event_id}', 'pid': None,
                        'message': message, 'raw': xml
                    })
                except Exception:
                    continue
        
        if not records:
            return pl.DataFrame()

        df = pl.DataFrame(records)
        return df.select([
            pl.col("timestamp").cast(pl.Datetime(time_unit="ms")),
            pl.col("host").cast(pl.Utf8),
            pl.col("process").cast(pl.Utf8),
            pl.lit(None, dtype=pl.Int64).alias("pid"),
            pl.col("message").cast(pl.Utf8),
            pl.col("raw").cast(pl.Utf8),
        ])

    @staticmethod
    def parse_from_filepaths(filepaths: List[Path]) -> pl.DataFrame:
        all_dfs = []
        for p in filepaths:
            try:
                if p.suffix.lower() == '.evtx':
                    df = LogParser.parse_evtx_logs(p)
                else:
                    text = p.read_text(errors='ignore').splitlines()
                    sample = '\n'.join(text[:10])

                    if sample.strip().startswith('{'):
                        df = LogParser.parse_json_logs(text)
                    # Check for syslog format (BSD or RFC5424)
                    elif SYSLOG_REGEX.search(sample) or RFC5424_REGEX.search(sample):
                        df = LogParser.parse_syslog_lines(text)
                    else:
                        df = LogParser.parse_generic_text(text)
                
                if not df.is_empty():
                    df = df.with_columns(pl.lit(str(p)).alias("source_file"))
                    all_dfs.append(df)
            except Exception as e:
                print(f"[parser] failed parsing {p}: {e}")
                continue

        if not all_dfs:
            return pl.DataFrame([])

        return pl.concat(all_dfs, how="vertical", rechunk=True)