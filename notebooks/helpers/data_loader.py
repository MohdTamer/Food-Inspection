from pathlib import Path

# This abstracts the file-structure of data folders
class DataLoader:
    BASE_DIR = Path('../../data')

    INTERIM_DIR = BASE_DIR / 'interim'
    PROCESSED_DIR = BASE_DIR / 'processed'

    @staticmethod
    def interim(filename: str) -> Path:
        return DataLoader.INTERIM_DIR / filename

    @staticmethod
    def processed(filename: str) -> Path:
        return DataLoader.PROCESSED_DIR / filename

STAGE1_PATH = Path('../../data/interim/cleaning/cleaning_stage1.csv')
STAGE1_LOG_PATH = Path('../../data/interim/cleaning/cleaning_stage1_log.csv')
STAGE2_PATH = Path('../../data/interim/cleaning/cleaning_stage2.csv')
STAGE2_LOG_PATH = Path('../../data/interim/cleaning/cleaning_stage2_log.csv')
PROCESSED_PATH = Path('../../data/processed/merged_inspections_licenses_inner_clean.csv')
PROCESSED_PARQUET_PATH = Path('../../data/processed/merged_inspections_licenses_inner_clean.parquet')
LOG_PATH = Path('../../data/interim/cleaning_log.csv')
QUARANTINE_PATH = Path('../../data/interim/quarantine.csv')
FINAL_LOG_PATH = Path('../../data/interim/cleaning_final_log.csv')