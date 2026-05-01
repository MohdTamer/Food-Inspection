from enum import Enum

class PipelineStage(Enum):
    RAW = "raw" # The og file donot overwrite under any circumstance
    INTERIM = "interim" # do whatever you like here
    CLEANED = "cleaned" # this is cleaned i.e. dropping nulls here
    PROCESSED = "processed" # this has feature engineering done to it
    QUARANTINED = "quarantined" # uggggh This guy someone look into it