import pandas as pd
from pathlib import Path

log_rows = []

def log_step(step: str, rows_before: int, rows_after: int, cols_before: int, cols_after: int, note: str = '') -> None:
    log_rows.append({
        'step': step,
        'rows_before': rows_before,
        'rows_after': rows_after,
        'rows_removed': rows_before - rows_after,
        'cols_before': cols_before,
        'cols_after': cols_after,
        'cols_removed': cols_before - cols_after,
        'note': note,
    })

def save_log(log_path: Path) -> None:
    log_df = pd.DataFrame(log_rows)
    log_df.to_csv(log_path, index=False)