from enum import Enum

class PipelineStage(Enum):
    RAW = "raw"
    INTERIM = "interim"
    CLEANED = "cleaned"
    PROCESSED = "processed"