"""
Loading, cleaning and list-splitting for data_final.xlsx.

The extraction sheet stores multi-valued fields as "; "-separated strings.
This module returns one publication per row with those fields parsed into
Python lists, after normalising whitespace and applying the fixes from
src.mappings.
"""

from pathlib import Path

import pandas as pd

from src.mappings import (
    ALGORITHM_CATEGORY, ALGORITHM_SYNONYMS, CATEGORY_FIXES, DISEASE_EXCLUDED,
    DISEASE_MAP, METRIC_SYNONYMS, REGION_CONTINENTS, REVIEW_LABELS, TARGET_GROUPS,
)

REQUIRED_COLUMNS = [
    'ID', 'Authors', 'Year', 'Title', 'DOI', 'Journal', 'Cat_Algorithms',
    'Algorithms', 'Countries', 'Diseases', 'Stage', 'Theme', 'Target',
    'Main_Metric_Type', 'Main_Metric_Value_min', 'Main_Metric_Value_max',
    'Notes', 'Sources',
]

# Optional reporting-quality columns used by Figure 6 when present.
OPTIONAL_COLUMNS = [
    'Validation', 'Spatial_blocked', 'Temporal_holdout',
    'Reports_AUPRC', 'Reports_SensSpec', 'Reports_CI', 'Reports_Calibration',
]

REVIEW_STAGE = 'Methodology/Review'


def _clean(value):
    """Collapse tabs/repeated spaces and strip; leave non-strings as is."""
    if isinstance(value, str):
        return ' '.join(value.split())
    return value


def split_list(value) -> list:
    """Split a "; "-separated cell into a de-duplicated, ordered list."""
    if not isinstance(value, str):
        return []
    items = [' '.join(part.split()) for part in value.split(';')]
    return list(dict.fromkeys(item for item in items if item))


def _to_number(value):
    return pd.to_numeric(value, errors='coerce')


def load_data(path: Path) -> pd.DataFrame:
    """Load data_final.xlsx and add parsed/standardised list columns."""
    df = pd.read_excel(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing columns: {missing}")

    keep = REQUIRED_COLUMNS + [c for c in OPTIONAL_COLUMNS if c in df.columns]
    df = df[keep].apply(lambda col: col.map(_clean))

    df['is_review'] = df['Stage'] == REVIEW_STAGE

    df['F2'] = df['Algorithms'].map(
        lambda v: list(dict.fromkeys(ALGORITHM_SYNONYMS.get(a, a) for a in split_list(v)
                                     if a not in REVIEW_LABELS)))
    unmapped = sorted(set(df['F2'].explode().dropna()) - set(ALGORITHM_CATEGORY))
    if unmapped:
        raise ValueError(f"Algorithms missing from ALGORITHM_CATEGORY: {unmapped}")
    # F1 is derived from F2 so that one rule per algorithm holds across all
    # figures; the extracted Cat_Algorithms is kept for the QA comparison.
    df['F1'] = df['F2'].map(
        lambda algs: list(dict.fromkeys(ALGORITHM_CATEGORY[a] for a in algs)))
    df['F1_declared'] = df['Cat_Algorithms'].map(
        lambda v: list(dict.fromkeys(CATEGORY_FIXES.get(c, c) for c in split_list(v)
                                     if c not in REVIEW_LABELS)))
    df['disease_list'] = df['Diseases'].map(
        lambda v: list(dict.fromkeys(DISEASE_MAP[d] for d in split_list(v) if d in DISEASE_MAP)))
    df['country_list'] = df['Countries'].map(
        lambda v: [c for c in split_list(v) if c not in REGION_CONTINENTS])
    df['region_list'] = df['Countries'].map(
        lambda v: [c for c in split_list(v) if c in REGION_CONTINENTS])
    df['source_list'] = df['Sources'].map(split_list)
    # One publication (ID 35) models two targets joined with " + ".
    df['target_list'] = df['Target'].map(
        lambda v: [t.strip() for t in v.split(' + ')] if isinstance(v, str) else [])
    df['target_group'] = df['target_list'].map(
        lambda ts: list(dict.fromkeys(TARGET_GROUPS[t] for t in ts if t in TARGET_GROUPS)))

    metric = df['Main_Metric_Type'].map(lambda v: METRIC_SYNONYMS.get(v, v))
    df['metric_type'] = metric.where(~metric.isin(REVIEW_LABELS))
    df['metric_min'] = df['Main_Metric_Value_min'].map(_to_number)
    df['metric_max'] = df['Main_Metric_Value_max'].map(_to_number)
    return df


def qa_report(df: pd.DataFrame) -> dict:
    """
    Tables for manual review of every mapping decision.

    Returns a dict of DataFrames (one per sheet): F2 mapping, F1/F2
    disagreements per publication, disease mapping and metric checks.
    """
    sheets = {}

    raw_f2 = df.loc[~df['is_review'], 'Algorithms'].map(split_list).explode().dropna()
    f2 = (raw_f2.to_frame('Raw algorithm (F2)')
          .assign(**{'Standardised': lambda t: t['Raw algorithm (F2)'].map(
              lambda a: ALGORITHM_SYNONYMS.get(a, a))})
          .assign(**{'Category (F1)': lambda t: t['Standardised'].map(ALGORITHM_CATEGORY)}))
    f2 = (f2.groupby(['Raw algorithm (F2)', 'Standardised', 'Category (F1)'], dropna=False)
          .size().rename('Publications').reset_index()
          .sort_values(['Category (F1)', 'Standardised']))
    sheets['F2 mapping'] = f2

    rows = []
    for _, r in df[~df['is_review']].iterrows():
        derived, declared = set(r['F1']), set(r['F1_declared'])
        if derived != declared:
            rows.append({
                'ID': r['ID'],
                'Cat_Algorithms (extracted F1)': r['Cat_Algorithms'],
                'Algorithms (F2)': r['Algorithms'],
                'Only in extracted F1': '; '.join(sorted(declared - derived)),
                'Only in F1 derived from F2 (used)': '; '.join(sorted(derived - declared)),
            })
    sheets['F1 vs F2'] = pd.DataFrame(rows)

    raw_d = df['Diseases'].map(split_list).explode().dropna()
    dis = raw_d.value_counts().rename('Publications').rename_axis('Raw disease').reset_index()
    dis['Figure label'] = dis['Raw disease'].map(DISEASE_MAP)
    dis['Status'] = dis['Raw disease'].map(
        lambda d: 'kept' if d in DISEASE_MAP else
        'excluded (non-WOAH / non-viral)' if d in DISEASE_EXCLUDED else 'UNKNOWN')
    sheets['Diseases'] = dis

    met = df[['ID', 'Main_Metric_Type', 'metric_type', 'Main_Metric_Value_min',
              'Main_Metric_Value_max', 'metric_min', 'metric_max']].copy()
    met['Flag'] = ''
    met.loc[met['metric_min'] > met['metric_max'], 'Flag'] = 'min > max'
    met.loc[met['metric_type'].notna() & met['metric_max'].isna(), 'Flag'] = 'no value'
    met.loc[met['metric_type'].notna() & met['metric_min'].isna()
            & met['metric_max'].notna(), 'Flag'] = 'only max given'
    met.loc[(met['metric_max'] > 1) & met['metric_type'].isin(['AUC', 'Accuracy', 'F1-Score']),
            'Flag'] = 'value > 1'
    sheets['Metrics'] = met

    raw_t = df.loc[~df['is_review'], 'target_list'].explode().dropna()
    tgt = raw_t.value_counts().rename('Publications').rename_axis('Raw target').reset_index()
    tgt['Target group'] = tgt['Raw target'].map(TARGET_GROUPS)
    sheets['Targets'] = tgt

    dup_id = df[df['ID'].duplicated(keep=False)]
    doi = df['DOI'].str.lower()
    dup_doi = df[doi.notna() & doi.duplicated(keep=False)]
    sheets['Duplicates'] = pd.concat([dup_id.assign(Issue='duplicate ID'),
                                      dup_doi.assign(Issue='duplicate DOI')])[
        ['ID', 'DOI', 'Title', 'Issue']]

    return sheets


def print_qa_summary(sheets: dict) -> None:
    unmapped = sheets['F2 mapping']['Category (F1)'].isna().sum()
    unknown_d = sheets['Diseases'].loc[sheets['Diseases']['Status'] == 'UNKNOWN', 'Raw disease']
    unknown_t = sheets['Targets'].loc[sheets['Targets']['Target group'].isna(), 'Raw target']
    print(f"    F2 algorithms without F1 category: {unmapped}")
    print(f"    Publications where F1 and F2 disagree: {len(sheets['F1 vs F2'])}")
    print(f"    Unknown disease labels: {len(unknown_d)}")
    print(f"    Metric rows flagged: {(sheets['Metrics']['Flag'] != '').sum()}")
    # Values not in the dictionaries are left out of the figures, so make
    # them impossible to miss.
    if len(unknown_d):
        print('    WARNING - disease labels not in DISEASE_MAP or DISEASE_EXCLUDED '
              f'(left out of disease figures): {list(unknown_d)}')
    if len(unknown_t):
        print('    WARNING - targets not in TARGET_GROUPS (left out of Figure 2C): '
              f'{list(unknown_t)}')
    if len(sheets['Duplicates']):
        print('    WARNING - duplicate IDs/DOIs: '
              f"{sheets['Duplicates'][['ID', 'Issue']].values.tolist()}")
