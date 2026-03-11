from typing import List, Dict, Any, Optional
from datetime import timedelta
from pydantic import BaseModel
from .parser import LogEntry

class TimelineEvent(BaseModel):
    timestamp: str
    severity: str
    message: str
    is_gap: bool = False
    gap_duration: Optional[str] = None

class AnalysisResult(BaseModel):
    root_cause_category: str
    timeline: List[TimelineEvent]
    total_gaps: int

# Keywords for categorization
KEYWORDS = {
    "DEPLOY": ["deploy", "reboot", "starting", "version", "deployment", "update"],
    "NETWORK": ["timeout", "connection", "dns", "unreachable", "refused", "latency"],
    "DB": ["postgres", "mysql", "database", "query", "deadlock", "db", "sql"],
    "CONFIG": ["missing key", "env", "environment", "invalid configuration", "config"],
}

def detect_root_cause(logs: List[LogEntry]) -> str:
    counts = {cat: 0 for cat in KEYWORDS}
    for log in logs:
        msg = log.message.lower()
        for cat, words in KEYWORDS.items():
            if any(word in msg for word in words):
                counts[cat] += 1
    
    # Return the category with highest match, or UNKNOWN
    best_cat = "UNKNOWN"
    max_count = 0
    for cat, count in counts.items():
        if count > max_count:
            max_count = count
            best_cat = cat
            
    return best_cat

def analyze_timeline(logs: List[LogEntry]) -> AnalysisResult:
    if not logs:
        return AnalysisResult(root_cause_category="UNKNOWN", timeline=[], total_gaps=0)

    timeline: List[TimelineEvent] = []
    total_gaps = 0
    
    # First entry
    timeline.append(TimelineEvent(
        timestamp=logs[0].timestamp.isoformat(),
        severity=logs[0].severity,
        message=logs[0].message
    ))

    for i in range(1, len(logs)):
        prev = logs[i-1]
        curr = logs[i]
        
        diff = curr.timestamp - prev.timestamp
        if diff > timedelta(minutes=5):
            total_gaps += 1
            timeline.append(TimelineEvent(
                timestamp=prev.timestamp.isoformat(),
                severity="GAP",
                message=f"Gap detected: {diff.total_seconds() / 60:.1f} mins of silence",
                is_gap=True,
                gap_duration=str(diff)
            ))
            
        timeline.append(TimelineEvent(
            timestamp=curr.timestamp.isoformat(),
            severity=curr.severity,
            message=curr.message
        ))

    root_cause = detect_root_cause(logs)
    
    return AnalysisResult(
        root_cause_category=root_cause,
        timeline=timeline,
        total_gaps=total_gaps
    )
