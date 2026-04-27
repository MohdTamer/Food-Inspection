import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

def profile(df: pd.DataFrame, label: str) -> pd.DataFrame:
    missing = df.isna().sum().sort_values(ascending=False)
    missing_pct = (missing / len(df) * 100).round(2)

    out = pd.DataFrame({
        'missing_count': missing,
        'missing_pct': missing_pct,
        'dtype': df.dtypes.astype(str)
    }).sort_values(['missing_count', 'dtype'], ascending=[False, True])

    print(f'=== {label} ===')
    print('shape:', df.shape)
    print('full duplicates:', int(df.duplicated().sum()))
    print('duplicate Inspection ID:', int(df.duplicated(subset=['Inspection ID']).sum()))
    return out