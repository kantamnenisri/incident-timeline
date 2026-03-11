import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class LogEntry(BaseModel):
    timestamp: datetime
    severity: str
    message: str

# Regex patterns
TIMESTAMP_PATTERNS = [
    r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?[Z+\d: ]*)", # ISO or YYYY-MM-DD HH:MM:SS
    r"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})", # Mar 11 12:00:00
]

SEVERITY_PATTERN = r"\b(INFO|WARN|WARNING|ERROR|CRITICAL|DEBUG|FATAL)\b"

def parse_timestamp(ts_str: str) -> Optional[datetime]:
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%b %d %H:%M:%S", # Syslog style (might need year suffix)
    ]
    
    ts_str = ts_str.strip()
    for fmt in formats:
        try:
            # For syslog style without year, assume current year
            if "%b" in fmt and "%Y" not in fmt:
                dt = datetime.strptime(ts_str, fmt)
                return dt.replace(year=datetime.now().year)
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    
    # Fallback to dateutil if available, but for now we'll stick to manual
    # Try ISO8601-ish manually
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except:
        return None

def parse_log_text(raw_text: str) -> List[LogEntry]:
    lines = raw_text.strip().split("\n")
    entries = []

    for line in lines:
        if not line.strip():
            continue

        ts = None
        for pattern in TIMESTAMP_PATTERNS:
            match = re.search(pattern, line)
            if match:
                ts = parse_timestamp(match.group(1))
                if ts:
                    break
        
        # Default to now if no timestamp found (though ideally we discard or group)
        if not ts:
            continue

        severity_match = re.search(SEVERITY_PATTERN, line, re.IGNORECASE)
        severity = severity_match.group(1).upper() if severity_match else "INFO"
        if severity == "WARNING":
            severity = "WARN"

        # Message is everything else or the whole line
        message = line.strip()
        
        entries.append(LogEntry(timestamp=ts, severity=severity, message=message))

    # Sort by timestamp
    entries.sort(key=lambda x: x.timestamp)
    return entries
