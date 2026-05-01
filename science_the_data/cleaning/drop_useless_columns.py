import pandas as pd

# I copied the comments are copied from the notebooks

COLS_TO_DROP = [
    # Exact duplicates of main dataset columns
    'BL_ADDRESS', 'BL_CITY', 'BL_STATE', 'BL_ZIP_CODE',
    'BL_LATITUDE', 'BL_LONGITUDE', 'BL_LOCATION',
    'BL_LEGAL_NAME', 'BL_DBA_NAME',

    # Administrative IDs with no predictive value
    'BL_ID', 'BL_LICENSE_ID', 'ACCOUNT NUMBER', 'SITE NUMBER',

    # Political/administrative boundaries
    'WARD', 'PRECINCT', 'WARD PRECINCT', 'POLICE DISTRICT', 'SSA',

    # Licensing process snapshots (not establishment state)
    'APPLICATION CREATED DATE', 'APPLICATION REQUIREMENTS COMPLETE',
    'PAYMENT DATE', 'CONDITIONAL APPROVAL',
    'LICENSE APPROVED FOR ISSUANCE', 'DATE ISSUED',
    'LICENSE STATUS CHANGE DATE',

    # Business activity — not used downstream
    'BUSINESS ACTIVITY ID', 'BUSINESS ACTIVITY',

    # Join keys — already served their purpose
    'LICENSE NUMBER', 'LICENSE CODE',

    # Redundant with COMMUNITY AREA NAME
    'NEIGHBORHOOD', 'COMMUNITY AREA',
]


def drop_useless_columns(
    df: pd.DataFrame,
    cols_to_drop: list[str] = COLS_TO_DROP,
) -> pd.DataFrame:
    present = [c for c in cols_to_drop if c in df.columns]
    missing = [c for c in cols_to_drop if c not in df.columns]

    if missing:
        # Warn but do not raise — upstream joins may legitimately omit some cols
        import warnings
        warnings.warn(
            f"drop_useless_columns: {len(missing)} requested column(s) not found "
            f"and will be skipped: {missing}",
            UserWarning,
            stacklevel=2,
        )

    return df.drop(columns=present)