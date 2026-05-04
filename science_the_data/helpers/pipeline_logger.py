from __future__ import annotations

import pandas as pd
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from science_the_data.helpers.types import LogEntry
    
class PipelineLogger:
    def __init__(self) -> None:
        self._entries: List[LogEntry] = []

    def log_step(
        self,
        step: str,
        rows_before: int,
        rows_after: int,
        cols_before: int,
        cols_after: int,
        note: str = "",
    ) -> None:
        entry = LogEntry(
            step=step,
            rows_before=rows_before,
            rows_after=rows_after,
            cols_before=cols_before,
            cols_after=cols_after,
            note=note,
        )
        self._entries.append(entry)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([asdict(e) for e in self._entries])

    def save(self, path: Path) -> None:
        self.to_dataframe().to_csv(path, index=False)

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)    