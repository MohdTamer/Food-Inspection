from pathlib import Path
from science_the_data.pipelines.types import PipelineStage

class PathResolver:
    """
    This abstracts the file-structure of data folders
    ** We assume the calling is the make file **
    ** or a terminal from the root directory **
    """
    DATA_DIR = Path('data')
    REPORT_DIR = Path('reports')
    
    MD_DIR = REPORT_DIR / "markdown"
    FIGURES = REPORT_DIR / "figures"

    RAW_DATA_DIR = DATA_DIR / 'raw'
    INTERIM_DATA_DIR = DATA_DIR / 'interim'
    CLEANED_DATA_DIR = DATA_DIR / 'cleaned'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    QUARANTINED_DATA_DIR = DATA_DIR / "quarantined"

    RAW_MD_REPORTS_DIR = MD_DIR / 'raw'
    INTERIM_MD_REPORTS_DIR = MD_DIR / 'interim'
    CLEANED_MD_REPORTS_DIR = MD_DIR / 'cleaned'
    PROCESSE_MD_REPORTS_DIR = MD_DIR / 'processed'

    @staticmethod
    def get_raw_data_path(filename: str) -> Path:
        return PathResolver.RAW_DATA_DIR / filename
    
    @staticmethod
    def get_cleaned_data_path(filename: str) -> Path:
        return PathResolver.CLEANED_DATA_DIR / filename
    
    @staticmethod
    def get_interim_data_path(filename: str) -> Path:
        return PathResolver.INTERIM_DATA_DIR / filename

    @staticmethod
    def get_processed_data_path(filename: str) -> Path:
        return PathResolver.PROCESSED_DATA_DIR / filename
    
    @staticmethod
    def get_quarintined_data_path(filename: str) -> Path:
        return PathResolver.QUARANTINED_DATA_DIR / filename
    
    @staticmethod
    def get_raw_report_path(filename: str) -> Path:
        return PathResolver.RAW_MD_REPORTS_DIR / filename
    
    @staticmethod
    def get_cleaned_report_path(filename: str) -> Path:
        return PathResolver.CLEANED_MD_REPORTS_DIR / filename
    
    @staticmethod
    def get_interim_report_path(filename: str) -> Path:
        return PathResolver.INTERIM_MD_REPORTS_DIR / filename

    @staticmethod
    def get_processed_report_path(filename: str) -> Path:
        return PathResolver.PROCESSE_MD_REPORTS_DIR / filename

    @staticmethod
    def get_data_path_from_stage(filename:str, stage: PipelineStage) -> Path:
        if stage == PipelineStage.RAW:
            csv_path = PathResolver.get_raw_data_path(filename)

        elif stage == PipelineStage.PROCESSED:
            csv_path = PathResolver.get_processed_data_path(filename)
        
        elif stage == PipelineStage.INTERIM:
            csv_path = PathResolver.get_interim_data_path(filename)

        elif stage == PipelineStage.CLEANED:
            csv_path = PathResolver.get_cleaned_data_path(filename)
            
        elif stage == PipelineStage.QUARANTINED:
            csv_path = PathResolver.get_quarintined_data_path(filename)

        else:
            raise ValueError(f"Unsupported stage: {stage}")

        return csv_path
    
    @staticmethod
    def get_report_path_from_stage(filename:str, stage: PipelineStage) -> Path:
        if stage == PipelineStage.RAW:
            report_path = PathResolver.get_raw_report_path(filename)

        elif stage == PipelineStage.PROCESSED:
            report_path = PathResolver.get_processed_report_path(filename)
        
        elif stage == PipelineStage.INTERIM:
            report_path = PathResolver.get_interim_report_path(filename)

        elif stage == PipelineStage.CLEANED:
            report_path = PathResolver.get_cleaned_report_path(filename)

        else:
            raise ValueError(f"Unsupported stage: {stage}")

        return report_path