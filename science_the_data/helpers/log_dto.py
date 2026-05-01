from __future__ import annotations

import pandas as pd
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import field

@dataclass
class LogEntry:
    step: str
    rows_before: int
    rows_after: int
    cols_before: int
    cols_after: int
    note: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def rows_removed(self) -> int:
        return self.rows_before - self.rows_after

    @property
    def cols_removed(self) -> int:
        return self.cols_before - self.cols_after