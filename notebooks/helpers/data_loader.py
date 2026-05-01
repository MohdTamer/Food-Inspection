from pathlib import Path

# This abstracts the file-structure of data folders
class DataLoader:
    BASE_DIR = Path('../../data')

    INTERIM_DIR = BASE_DIR / 'interim'
    PROCESSED_DIR = BASE_DIR / 'processed'
    RAW_DIR = BASE_DIR / 'raw'
    CLEANED_DIR = BASE_DIR / "cleaned"
    TRANSFORMED_DIR = BASE_DIR / 'transformed'

    @staticmethod
    def interim(filename: str) -> Path:
        return DataLoader.INTERIM_DIR / filename

    @staticmethod
    def raw(filename: str) -> Path:
        return DataLoader.RAW_DIR / filename
    
    @staticmethod
    def processed(filename: str) -> Path:
        return DataLoader.PROCESSED_DIR / filename
    
    @staticmethod
    def cleaned(filename: str) -> Path:
        return DataLoader.CLEANED_DIR / filename

    @staticmethod
    def transformed(filename: str) -> Path:
        DataLoader.TRANSFORMED_DIR.mkdir(parents=True, exist_ok=True)
        return DataLoader.TRANSFORMED_DIR / filename

STAGE1_PATH = Path('../../data/interim/cleaning/cleaning_stage1.csv')
STAGE1_LOG_PATH = Path('../../data/interim/cleaning/cleaning_stage1_log.csv')
STAGE2_PATH = Path('../../data/interim/cleaning/cleaning_stage2.csv')
STAGE2_LOG_PATH = Path('../../data/interim/cleaning/cleaning_stage2_log.csv')
PROCESSED_PATH = Path('../../data/processed/merged_inspections_licenses_inner_clean.csv')
PROCESSED_PARQUET_PATH = Path('../../data/processed/merged_inspections_licenses_inner_clean.parquet')
TRAIN_CSV_PATH = Path('../../data/processed/train.csv')
TRAIN_PARQUET_PATH = Path('../../data/processed/train.parquet')
TEST_CSV_PATH = Path('../../data/processed/test.csv')
TEST_PARQUET_PATH = Path('../../data/processed/test.parquet')
LOG_PATH = Path('../../data/interim/cleaning_log.csv')
QUARANTINE_PATH = Path('../../data/interim/quarantine.csv')
FINAL_LOG_PATH = Path('../../data/interim/cleaning_final_log.csv')