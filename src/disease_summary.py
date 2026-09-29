"""
Disease summary table: one row per Disease_standardized category,
aggregating stage distribution, top algorithms, top countries, year range
and publication counts - built entirely from the same standardized
dataframes the figures and Table S2 are built from (see main.py).
"""

import json
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

# (full category name, short label used in the "Stage distribution" column)
STAGE_ORDER = [
    ('Prediction/Forecasting', 'Prediction'),
    ('Surveillance', 'Surveillance'),
    ('Spatial Modeling', 'Spatial'),
    ('Field', 'Field'),
    ('Diagnostics', 'Diagnostics'),
    ('Other', 'Other'),
    ('Methodology/Review', 'Methodology'),
]

# "Key application" is not free-text-mined from the paper - it's the
# readable label for whichever Stage category is most common for that
# disease, so it stays fully traceable to the Stage distribution column
# rather than being independently guessed.
STAGE_TO_APPLICATION = {
    'Prediction/Forecasting': 'Outbreak prediction/forecasting',
    'Surveillance': 'Disease surveillance/early detection',
    'Diagnostics': 'Diagnostic classification',
    'Field': 'Field deployment/validation',
    'Spatial Modeling': 'Spatial risk mapping',
    'Methodology/Review': 'Methodological review',
    'Other': 'Other/mixed applications',
}

ALGORITHM_ABBREVIATIONS = {
    'Random Forest': 'RF',
    'XGBoost': 'XGB',
    'Deep Learning': 'DL',
    'SVM': 'SVM',
    'Spatial/GIS': 'GIS',
    'Bayesian': 'Bayes',
    'NLP': 'NLP',
    'Logistic Regression': 'LogReg',
    'Ensemble': 'Ens',
    'Decision Tree': 'DT',
    'KNN': 'KNN',
    'Time Series': 'TS',
    'Statistical Regression': 'StatReg',
    'Network Analysis': 'NetAnl',
    'Feature Selection': 'FeatSel',
    'K-Means': 'KMeans',
}


def _all_counts_str(series: pd.Series, abbreviations: dict = None) -> str:
    """'RF(22), DL(18), XGB(18), GIS(4), ...'-style string - every distinct
    value that occurs, most common first (no top-N cutoff)."""
    counts = series.dropna().value_counts()
    if counts.empty:
        return ''
    labels = (abbreviations or {})
    return ', '.join(f"{labels.get(value, value)}({count})" for value, count in counts.items())


def _stage_distribution_str(stage_counts: pd.Series) -> str:
    """Only stages with at least one publication - a zero entry adds nothing
    a reader needs and just pads out every row to the same 7 items."""
    parts = [f"{short}({int(stage_counts[full])})" for full, short in STAGE_ORDER if stage_counts.get(full, 0) > 0]
    return ', '.join(parts)


def build_disease_summary(df_pub: pd.DataFrame, df_disease_mentions: pd.DataFrame,
                           df_algo_disease: pd.DataFrame, df_country_disease: pd.DataFrame) -> pd.DataFrame:
    """
    Build the disease summary table (see module docstring for sourcing).

    Every per-disease column here is mention-based, from
    resolve_disease_categories() (src/standardization_mappings.py): a
    publication naming 1-3 distinct diseases counts toward each of them
    (e.g. "ASF, HPAI" contributes to both ASF's and HPAI's row); 4+ distinct
    diseases collapse to 'General' instead of being split further. So n does
    NOT sum to len(df_pub), and % (n / 163 publications) does not sum to
    100% - a multi-disease publication is deliberately counted more than
    once, the same way Figure 2/4 already count multi-algorithm mentions.

    n / Stage distribution / Year range: df_disease_mentions
        (apply_disease_standardization(df) output - one row per
        (publication, disease) mention, Stage/Year carried through from the
        original row). Stage distribution omits zero-count stages.
    Algorithms: every algorithm category mentioned for that disease (no
        top-N cutoff), from df_algo_disease
        (apply_algorithm_disease_standardization, Figure 2's source).
    Countries: every country mentioned for that disease, from
        df_country_disease (apply_country_disease_standardization).
    TOTAL row: df_pub (apply_publication_level_standardization) - the true
        163-publication aggregate, unaffected by any multi-disease counting.

    Args:
        df_pub: apply_publication_level_standardization(df) output.
        df_disease_mentions: apply_disease_standardization(df) output.
        df_algo_disease: apply_algorithm_disease_standardization(df) output.
        df_country_disease: apply_country_disease_standardization(df) output.

    Returns:
        DataFrame sorted by n descending, with a trailing TOTAL row.
    """
    total_publications = len(df_pub)
    rows = []
    for disease, group in df_disease_mentions.groupby('Disease_standardized'):
        stage_counts = group['Stage_standardized'].value_counts()
        algo_rows = df_algo_disease.loc[df_algo_disease['Disease_standardized'] == disease, 'Algorithm_standardized']
        country_rows = df_country_disease.loc[df_country_disease['Disease_standardized'] == disease, 'Country_standardized']

        year_min, year_max = int(group['Year'].min()), int(group['Year'].max())
        top_stage = stage_counts.idxmax() if not stage_counts.empty else None

        rows.append({
            'Disease': disease,
            'n': len(group),
            '%': round(len(group) / total_publications * 100, 1),
            'Stage distribution': _stage_distribution_str(stage_counts),
            'Algorithms': _all_counts_str(algo_rows, ALGORITHM_ABBREVIATIONS),
            'Countries': _all_counts_str(country_rows),
            'Year range': f"{year_min}–{year_max}" if year_min != year_max else str(year_min),
            'Key application': STAGE_TO_APPLICATION.get(top_stage, ''),
            'avg_year': round(group['Year'].mean(), 1),
        })

    summary = pd.DataFrame(rows).sort_values('n', ascending=False).reset_index(drop=True)

    total_stage_counts = df_pub['Stage_standardized'].value_counts()
    total_row = pd.DataFrame([{
        'Disease': 'TOTAL (unique publications)',
        'n': total_publications,
        '%': 100.0,
        'Stage distribution': _stage_distribution_str(total_stage_counts),
        'Algorithms': _all_counts_str(df_algo_disease['Algorithm_standardized'], ALGORITHM_ABBREVIATIONS),
        'Countries': _all_counts_str(df_country_disease['Country_standardized']),
        'Year range': f"{int(df_pub['Year'].min())}–{int(df_pub['Year'].max())}",
        'Key application': '',
        'avg_year': round(df_pub['Year'].mean(), 1),
    }])

    return pd.concat([summary, total_row], ignore_index=True)


DISPLAY_COLUMNS = ['Disease', 'n', '%', 'Stage distribution', 'Algorithms',
                    'Countries', 'Year range', 'Key application']

COLUMN_WIDTHS = {
    'Disease': 16, 'n': 6, '%': 8, 'Stage distribution': 45,
    'Algorithms': 55, 'Countries': 70, 'Year range': 12,
    'Key application': 30,
}


def to_markdown_table(summary: pd.DataFrame) -> str:
    display_cols = DISPLAY_COLUMNS
    df = summary[display_cols].copy()
    df['%'] = df['%'].map(lambda v: f"{v:.1f}")

    widths = {c: max(len(c), df[c].astype(str).map(len).max()) for c in display_cols}
    header = '| ' + ' | '.join(c.ljust(widths[c]) for c in display_cols) + ' |'
    sep = '|-' + '-|-'.join('-' * widths[c] for c in display_cols) + '-|'
    body = [
        '| ' + ' | '.join(str(row[c]).ljust(widths[c]) for c in display_cols) + ' |'
        for _, row in df.iterrows()
    ]
    return '\n'.join([header, sep] + body)


def save_disease_summary_excel(summary: pd.DataFrame, output_path: Path) -> None:
    """Styled .xlsx version, matching Table S2's look (src/table_generator.py)."""
    df = summary[DISPLAY_COLUMNS].copy()

    wb = Workbook()
    ws = wb.active
    ws.title = "Disease Summary"

    header_fill = PatternFill(start_color="2E4057", end_color="2E4057", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    total_fill = PatternFill(start_color="E8EAED", end_color="E8EAED", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin'),
    )

    for col_num, col_name in enumerate(DISPLAY_COLUMNS, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = col_name
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border

    for row_idx, row in df.iterrows():
        is_total = str(row['Disease']).startswith('TOTAL')
        for col_num, col_name in enumerate(DISPLAY_COLUMNS, 1):
            cell = ws.cell(row=row_idx + 2, column=col_num)
            cell.value = row[col_name]
            cell.border = thin_border
            cell.alignment = Alignment(vertical='top', wrap_text=True)
            if is_total:
                cell.fill = total_fill
                cell.font = Font(bold=True, size=11)

    for col_num, col_name in enumerate(DISPLAY_COLUMNS, 1):
        ws.column_dimensions[ws.cell(row=1, column=col_num).column_letter].width = COLUMN_WIDTHS.get(col_name, 14)

    ws.freeze_panes = "A2"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)


def save_disease_summary(summary: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / 'Table_Disease_Summary.csv'
    summary[DISPLAY_COLUMNS].to_csv(csv_path, index=False)

    md_path = output_dir / 'Table_Disease_Summary.md'
    md_path.write_text(to_markdown_table(summary) + '\n')

    json_path = output_dir / 'Table_Disease_Summary.json'
    json_path.write_text(json.dumps(summary[DISPLAY_COLUMNS].to_dict(orient='records'), indent=2, ensure_ascii=False))

    xlsx_path = output_dir / 'Table_Disease_Summary.xlsx'
    save_disease_summary_excel(summary, xlsx_path)

    is_total = summary['Disease'].str.startswith('TOTAL')
    mention_sum = summary.loc[~is_total, 'n'].sum()
    total_pubs = int(summary.loc[is_total, 'n'].iloc[0])

    print(f"\n  Disease summary table ({(~is_total).sum()} diseases + TOTAL):")
    print(f"    CSV:      {csv_path}")
    print(f"    Markdown: {md_path}")
    print(f"    JSON:     {json_path}")
    print(f"    Excel:    {xlsx_path}")
    print(f"    n is mention-based (resolve_disease_categories): sum={mention_sum} vs {total_pubs} unique publications "
          f"({mention_sum - total_pubs:+d}, from publications naming 2-3 diseases)")

    print("\n  Per-disease stats:")
    for _, row in summary[~is_total].iterrows():
        print(f"    {row['Disease']}: {row['n']} publikacji, średni rok: {row['avg_year']}")


if __name__ == '__main__':
    import sys
    ROOT = Path(__file__).resolve().parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from src.data_cleaning import load_data, remove_excluded
    from src.standardization import (
        apply_publication_level_standardization,
        apply_disease_standardization,
        apply_algorithm_disease_standardization,
        apply_country_disease_standardization,
    )

    df = remove_excluded(load_data(Path('data/data_ml_publications.xlsx')))
    df_pub = apply_publication_level_standardization(df)
    df_disease_mentions = apply_disease_standardization(df)
    df_algo_disease = apply_algorithm_disease_standardization(df)
    df_country_disease = apply_country_disease_standardization(df)

    summary = build_disease_summary(df_pub, df_disease_mentions, df_algo_disease, df_country_disease)
    save_disease_summary(summary, Path('output'))
