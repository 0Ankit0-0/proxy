import polars as pl
import re
from pathlib import Path
from typing import List, Optional
import datetime as dt
import json
import pandas as pd

SYSLOG_REGEX = re.compile(
    r'^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<proc>\S+?)(?:\[(?P<pid>\d+)\])?:\s+(?P<msg>.*)$'
)

MONTH_MAP = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}


class LogParser:
    """
    Parser Service - transform raw log lines/files to structured Polars DataFrames.

    Provided parsers:
    - parse_syslog_lines: regex-based syslog parser which extracts timestamp, host, process, pid, message
    - parse_generic_text: simple fallback that keeps timestamp (if found) + message
    - parse_json_logs: Parse JSON-formatted logs (common in modern apps)
    - parse_from_filepaths: convenience to detect file type and parse into a single Polars DataFrame

    Design notes:
    - Uses polars for columnar speed and memory efficiency.
    - Parsers are modular: add new functions for EVTX, Apache, Nginx, or LogHub formats.
    """

    @staticmethod
    def _make_timestamp_from_syslog(month: str, day: str, time: str) -> Optional[dt.datetime]:
        """Construct a datetime object from syslog components."""
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
        """
        Parse a list of syslog text lines into a Polars DataFrame.
        Columns: timestamp, host, process, pid, message, raw
        """
        record = []
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue

            m = SYSLOG_REGEX.match(ln)
            if m:
                ts = LogParser._make_timestamp_from_syslog(m.group('month'), m.group('day'), m.group('time'))
                rec = {
                    "timestamp": ts,
                    "host": m.group("host"),
                    "process": m.group("proc"),
                    "pid": int(m.group("pid")) if m.group("pid") else None,
                    "message": m.group("msg"),
                    "raw": ln
                }
            else:
                rec = {
                    "timestamp": None,
                    "host": None,
                    "process": None,
                    "pid": None,
                    "message": ln,
                    "raw": ln
                }
            record.append(rec)

        df = pl.DataFrame(record).with_columns([
            pl.col("timestamp").cast(pl.Datetime(time_unit = "ms")),
            pl.col("host").cast(pl.Utf8),
            pl.col("process").cast(pl.Utf8),
            pl.col("pid").cast(pl.Utf8),
            pl.col("message").cast(pl.Utf8),
            pl.col("raw").cast(pl.Utf8),
        ])

        return df

    @staticmethod
    def parse_generic_text(lines: List[str]) -> pl.DataFrame:
        """ Very simple parser: attempt to find ISO-like timestamp, otherwise keep raw.
        Columns: timestamp, host, process, pid, message, raw
        """

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
                "timestamp": ts,
                "host": None,
                "process": None,
                "pid": None,
                "message": ln,
                "raw": ln
            })

        df = pl.DataFrame(records).with_columns([
            pl.col("timestamp").cast(pl.Datetime(time_unit = "ms")),
            pl.col("host").cast(pl.Utf8),
            pl.col("process").cast(pl.Utf8),
            pl.col("pid").cast(pl.Utf8),
            pl.col("message").cast(pl.Utf8),
            pl.col("raw").cast(pl.Utf8),
        ])

        return df

    @staticmethod
    def parse_json_logs(lines: List[str]) -> pl.DataFrame:
        """Parse JSON-formatted logs (common in modern apps)"""
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
            pl.col("pid").cast(pl.Utf8),
            pl.col("message").cast(pl.Utf8),
            pl.col("raw").cast(pl.Utf8),
        ])

        return df

    @staticmethod
    def parse_from_filepaths(filepaths: List[Path]) -> pl.DataFrame:
        """
        Given one or more file paths, detect type and parse into a single Polars DataFrame.
        Detection heuristics:
            - If file contains 'syslog' or lines match syslog regex -> parse_syslog_lines
            - Otherwise fallback to parse_generic_text
        """

        all_dfs = []
        for p in filepaths:
            try:
                text = p.read_text(errors='ignore').splitlines()
                sample = '\n'.join(text[: 10])

                # Try JSON first
                if sample.strip().startswith('{'):
                    df = LogParser.parse_json_logs(text)
                    df = df.with_columns(pl.lit(str(p)).alias("source_file"))
                    all_dfs.append(df)
                elif SYSLOG_REGEX.search(sample):
                    df = LogParser.parse_syslog_lines(text)
                    df = df.with_columns(pl.lit(str(p)).alias("source_file"))
                    all_dfs.append(df)
                else:
                    df = LogParser.parse_generic_text(text)
                    df = df.with_columns(pl.lit(str(p)).alias("source_file"))
                    all_dfs.append(df)
            except Exception as e:
                print(f"[parsed] failed parsing {p}: {e}")
                continue

        if not all_dfs:
            return pl.DataFrame([])

        combined = pl.concat(all_dfs, how = "vertical", rechunk = True)
        return combined





        
                
    