from pathlib import Path

class PathResolver:
    """
    This abstracts the file-structure of data folders
    ** We assume the calling is the make file **
    ** or a terminal from the root directory **
    """
    BASE_DIR = Path('data')

    RAW_DIR = BASE_DIR / 'raw'
    INTERIM_DIR = BASE_DIR / 'interim'
    PROCESSED_DIR = BASE_DIR / 'processed'

    @staticmethod
    def raw(filename: str) -> Path:
        return PathResolver.RAW_DIR / filename
    
    @staticmethod
    def interim(filename: str) -> Path:
        return PathResolver.INTERIM_DIR / filename

    @staticmethod
    def processed(filename: str) -> Path:
        return PathResolver.PROCESSED_DIR / filename
    
