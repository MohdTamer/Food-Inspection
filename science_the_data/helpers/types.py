from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

import pandas as pd


@dataclass
class LogEntry:
    step: str
    rows_before: int
    rows_after: int
    cols_before: int
    cols_after: int
    note: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def rows_removed(self) -> int:
        return self.rows_before - self.rows_after

    @property
    def cols_removed(self) -> int:
        return self.cols_before - self.cols_after


@dataclass
class SplitData:
    df: pd.DataFrame
    file_name: str


@dataclass
class DataSplits:
    """Holds the three CSV file names that travel through the post-split pipelines."""

    train: str
    val: str
    test: str

    def as_tuple(self) -> tuple[str, str, str]:
        return self.train, self.val, self.test

    def map(self, fn) -> "DataSplits":
        return DataSplits(fn(self.train), fn(self.val), fn(self.test))


class PipelineStage(Enum):
    RAW = "raw"  # The og file donot overwrite under any circumstance
    INTERIM = "interim"  # do whatever you like here
    CLEANED = "cleaned"  # this is cleaned i.e. dropping nulls here
    PROCESSED = "processed"  # this has feature engineering done to it
    QUARANTINED = "quarantined"  # uggggh This guy someone look into it
