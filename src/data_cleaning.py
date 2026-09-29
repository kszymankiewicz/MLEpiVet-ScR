"""
Data loading for PRISMA-ScR scoping review.
"""

import pandas as pd
from pathlib import Path

# Legacy pre-computed columns present in the raw export; the pipeline
# recomputes these itself via src.standardization, so they are dropped
# on load to avoid duplicate/stale "*_Standardized" columns downstream.
LEGACY_STANDARDIZED_COLUMNS = [
    'Algorithm_Standardized', 'Country_Standardized',
    'Disease_Standardized', 'Stage_Standardized',
]


def load_data(path: Path) -> pd.DataFrame:
    """Load the raw bibliography Excel file."""
    df = pd.read_excel(path)
    return df.drop(columns=[c for c in LEGACY_STANDARDIZED_COLUMNS if c in df.columns])


def remove_excluded(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only records with Status == 'included'."""
    return df[df['Status'] == 'included'].copy().reset_index(drop=True)
