"""
Data standardization module for PRISMA-ScR scoping review.
Handles expansion of multi-value fields and mapping to standard categories.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict

from src.standardization_mappings import (
    map_algorithm_display,
    map_algorithms_multilabel,
    map_disease_display,
    resolve_disease_categories,
    map_stage,
    map_country,
)

def _mask_parens(text: str) -> str:
    """
    Same-length copy of text with every character inside (parentheses)
    replaced by a placeholder - used to find separator positions that fall
    OUTSIDE parens, without disturbing the original string's indices.
    """
    out = []
    depth = 0
    for ch in text:
        if ch == '(':
            depth += 1
            out.append('\x00')
        elif ch == ')':
            depth = max(0, depth - 1)
            out.append('\x00')
        elif depth > 0:
            out.append('\x00')
        else:
            out.append(ch)
    return ''.join(out)


def parse_field(field_value: str, separator: str = ',') -> list:
    """
    Parse comma/slash-separated field into list of values.
    Rozpoznaje: , / ; and or + | i

    Splits only on separators that fall outside parentheses, so a
    parenthetical aside containing its own comma/semicolon (e.g. "Bovine
    tuberculosis (bTB; Mycobacterium bovis)", or an illustrative list like
    "zoonotic diseases (including HPAI, West Nile fever, Ebola, ...)")
    isn't torn into unrelated single-word fragments that then get
    individually - and wrongly - mapped to disease/algorithm/country
    categories they don't belong to.
    """
    if pd.isna(field_value):
        return []

    field_str = str(field_value).strip()

    # Jeśli zawiera review marker - nie rozszerzaj
    if any(word in field_str.lower() for word in ['review of', 'review:', 'discusses', 'conceptual only', 'no machine learning']):
        return [field_str]  # Zwróć oryginalny tekst - będzie zmapowany na "Other"

    # Szukaj separatorów (tylko poza nawiasami). ' i ' obok ' and '/' or ' -
    # polski spójnik na końcu wyliczenia (np. "Syria i United Arab
    # Emirates."), bo dane wejściowe mieszają PL/EN.
    masked = _mask_parens(field_str)
    separators = [';', ',', '/', ' and ', ' or ', ' i ', '+', '|']
    found_sep = None

    for sep in separators:
        if sep in masked:
            found_sep = sep
            break

    if found_sep:
        items = []
        start = 0
        idx = masked.find(found_sep, start)
        while idx != -1:
            items.append(field_str[start:idx])
            start = idx + len(found_sep)
            idx = masked.find(found_sep, start)
        items.append(field_str[start:])
    else:
        items = [field_str]

    # Oxford-comma-less tail: "A, B, C and D" (or "...C i D") only splits on
    # ',' above, since only one separator type is used per string - leaving
    # the last two items merged as "C and D"/"C i D". Split that tail
    # further on whichever conjunction it contains, as long as a
    # conjunction wasn't already the primary separator (which would mean
    # it's already been split throughout).
    conjunctions = [' and ', ' or ', ' i ']
    if found_sep and found_sep not in conjunctions and items:
        last_masked = _mask_parens(items[-1])
        for conj in conjunctions:
            if conj in last_masked:
                idx = last_masked.find(conj)
                items = items[:-1] + [items[-1][:idx], items[-1][idx + len(conj):]]
                break

    # Wyczyść każdy element (spacje + końcowa kropka po ostatniej pozycji
    # wyliczenia, np. "United Arab Emirates.")
    cleaned = [item.strip().rstrip('.').strip() for item in items if item.strip()]
    return cleaned if cleaned else [field_value]


def apply_publication_level_standardization(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per publication, exactly matching Table S2
    (src/table_generator.py): Country/Stage each get one category via the
    map_* functions applied directly to the raw field, with no row
    expansion. Algorithm_standardized and Disease_standardized are the
    exception - each is every category map_algorithms_multilabel /
    map_diseases_multilabel finds in the raw field, joined with '; ' (via
    map_algorithm_display / map_disease_display):
      - a publication can genuinely use several algorithms at once (e.g.
        "Random Forest (RF); Boosted Regression Tree (BRT)" -> "Random
        Forest; XGBoost"), and forcing a single first-match category
        silently dropped the others and disagreed with how Figures 2/4
        count algorithms.
      - likewise a publication can genuinely cover 2-3 named diseases (e.g.
        "ASF, HPAI" -> "ASF; HPAI"); resolve_disease_categories() collapses
        4+ distinct detected categories to 'General' (too diffuse to name
        individually) rather than picking whichever one a fixed keyword
        priority order happened to check first - see the comment above
        DISEASE_STANDARDIZATION_KEY in standardization_mappings.py for the
        "Fourteen priority zoonotic diseases (including HPAI, West Nile
        fever, ...)" case that motivated this.

    Use this - not apply_standardization()'s output - for any figure where a
    publication must count exactly once (Figure 1 temporal trend, Figure 5
    stage distribution). apply_standardization() expands rows by disease x
    country combinations; Year and Stage are single-valued per publication
    but get silently duplicated across those expanded rows too (a
    publication with 2 diseases and 2 countries appears 4x), which inflates
    any figure built on it that isn't itself about disease/country
    frequency - this was the source of Figure 1/5 publication counts (208
    and 191 rows respectively) not matching Table S2's 163.

    Args:
        df: Input DataFrame (filtered to Status='included').
    """
    df_copy = df.copy()
    df_copy['Disease_standardized'] = df_copy['Disease'].apply(map_disease_display)
    df_copy['Country_standardized'] = df_copy['Country'].apply(map_country)
    df_copy['Algorithm_standardized'] = df_copy['Algorithm(s)'].apply(map_algorithm_display)
    df_copy['Stage_standardized'] = df_copy['Stage'].apply(map_stage)
    return df_copy


def expand_multivalued_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand rows based on multiple diseases, countries, and algorithms.
    """
    expanded_rows = []
    
    for idx, row in df.iterrows():
        # Parse fields
        diseases = parse_field(row['Disease'])
        countries = parse_field(row['Country'])
        algorithms = parse_field(row['Algorithm(s)'])
        
        # Collapse based on count
        if len(diseases) >= 3:
            diseases = ['General']
        elif len(diseases) == 0:
            diseases = ['Unknown']
        
        if len(countries) >= 3:
            countries = ['International']
        elif len(countries) == 0:
            countries = ['Unknown']
        
        # ALGORITHMS: CRUCIAL FIX
        if len(algorithms) >= 3:
            algorithms = ['Other']
        elif len(algorithms) == 0:
            algorithms = ['Unknown']
        # NOTE: 2 algorithms stay as 2 separate entries after expansion
        
        # Create rows for all combinations
        for disease in diseases:
            for country in countries:
                for algorithm in algorithms:
                    new_row = row.copy()
                    new_row['Disease'] = disease.strip()
                    new_row['Country'] = country.strip()
                    new_row['Algorithm(s)'] = algorithm.strip()
                    expanded_rows.append(new_row)
    
    df_expanded = pd.DataFrame(expanded_rows).reset_index(drop=True)
    return df_expanded


def expand_algorithms_multilabel(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per algorithm category detected anywhere in the raw Algorithm(s)
    text (whole-string substring search via map_algorithms_multilabel - see
    src/standardization_mappings.py). A publication can match several
    categories at once; publications with no match contribute zero rows.
    This matches the legacy standalone standardization script's counting
    method exactly.

    Disease/Country are left untouched (not expanded): this view is for
    Figure 4 (top algorithms overall), which has no disease/country
    dimension, so it must not multiply rows - and inflate algorithm counts -
    for publications that also happen to cover multiple diseases/countries.
    """
    expanded_rows = []

    for idx, row in df.iterrows():
        for category in map_algorithms_multilabel(row['Algorithm(s)']):
            new_row = row.copy()
            new_row['Algorithm_standardized'] = category
            expanded_rows.append(new_row)

    return pd.DataFrame(expanded_rows).reset_index(drop=True)


def expand_algorithms_and_disease_multilabel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand rows by both Disease (multi-label, via resolve_disease_categories
    - 1-3 distinct detected categories kept separate, 4+ collapsed to
    'General') and algorithm category (multi-label, via
    map_algorithms_multilabel). Used exclusively for Figure 2 (algorithm vs
    disease heatmap), which needs both dimensions.
    """
    expanded_rows = []

    for idx, row in df.iterrows():
        diseases = resolve_disease_categories(row['Disease'])
        categories = map_algorithms_multilabel(row['Algorithm(s)'])

        for disease in diseases:
            for category in categories:
                new_row = row.copy()
                new_row['Disease_standardized'] = disease
                new_row['Algorithm_standardized'] = category
                expanded_rows.append(new_row)

    return pd.DataFrame(expanded_rows).reset_index(drop=True)


def apply_algorithm_standardization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Multi-label algorithm standardization for Figure 4 (top algorithms).
    One row per (publication, algorithm category) mention - no disease
    dimension, no Stage filtering (review exclusion already happens inside
    map_algorithms_multilabel, matching the legacy script).

    Args:
        df: Input DataFrame (filtered to Status='included'), not yet
            expanded by apply_standardization().
    """
    df_expanded = expand_algorithms_multilabel(df)

    with_algorithms = df['Algorithm(s)'].apply(lambda v: len(map_algorithms_multilabel(v)) > 0).sum()
    print(f"\n  [multi-label] Publications with algorithms: {with_algorithms}")
    print(f"  [multi-label] Publications without algorithms: {len(df) - with_algorithms}")
    print(f"  [multi-label] Algorithm mentions counted: {len(df_expanded)}")

    return df_expanded


def verify_algorithm_consistency(df_pub: pd.DataFrame, df_algo: pd.DataFrame) -> int:
    """
    Cross-check that Table S2's per-publication Algorithm_standardized
    (map_algorithm_display, one joined string) and Figure 2/4's per-mention
    Algorithm_standardized (map_algorithms_multilabel, one row per category)
    agree on the exact same set of categories for every publication - they
    are two independently-shaped views over the same map_algorithms_multilabel
    call, so any divergence would mean the two figures/table are telling a
    reader different things about the same publication.

    Joins on DOI rather than row position: expand_algorithms_multilabel()
    resets the index during expansion, so positional alignment with df_pub
    silently compares the wrong rows once any publication expands to more
    or fewer than 1 row.

    Args:
        df_pub: apply_publication_level_standardization(df) output (Table S2).
        df_algo: apply_algorithm_standardization(df) output (Figure 4).

    Returns:
        Number of publications where the two views disagree (0 = consistent).
    """
    fig_categories_by_doi = df_algo.groupby('DOI')['Algorithm_standardized'].apply(set).to_dict()

    mismatches = []
    for _, row in df_pub.iterrows():
        table_categories = set(row['Algorithm_standardized'].split('; ')) if pd.notna(row['Algorithm_standardized']) else set()
        fig_categories = fig_categories_by_doi.get(row['DOI'], set())
        if table_categories != fig_categories:
            mismatches.append((row['DOI'], row['Algorithm(s)'], table_categories, fig_categories))

    print(f"\n  [QA] Algorithm mapping consistency (Table S2 vs Figure 2/4): "
          f"{len(df_pub) - len(mismatches)}/{len(df_pub)} publications agree")
    for doi, raw, table_categories, fig_categories in mismatches:
        print(f"    MISMATCH {doi}: Table S2={table_categories} vs Fig2/4={fig_categories} | raw={raw!r}")

    return len(mismatches)


def apply_algorithm_disease_standardization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Multi-label algorithm x disease standardization for Figure 2 (heatmap).
    One row per (publication, disease, algorithm category) mention.

    Args:
        df: Input DataFrame (filtered to Status='included'), not yet
            expanded by apply_standardization().
    """
    return expand_algorithms_and_disease_multilabel(df)


def expand_countries_and_disease_multilabel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand rows by both Disease (multi-label, via resolve_disease_categories
    - see expand_algorithms_and_disease_multilabel) and Country (multi-label,
    no collapsing threshold - matches expand_countries_multilabel()). Used
    for the disease summary table's "Top countries per disease" column.
    """
    expanded_rows = []

    for idx, row in df.iterrows():
        diseases = resolve_disease_categories(row['Disease'])
        countries = parse_field(row['Country'])

        if len(countries) == 0:
            countries = ['Unknown']

        for disease in diseases:
            for country in countries:
                new_row = row.copy()
                new_row['Disease_standardized'] = disease
                new_row['Country'] = country.strip()
                expanded_rows.append(new_row)

    return pd.DataFrame(expanded_rows).reset_index(drop=True)


def apply_country_disease_standardization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Multi-label country x disease standardization for the disease summary
    table's "Top countries per disease" column. One row per (publication,
    disease, country) mention.

    Args:
        df: Input DataFrame (filtered to Status='included'), not yet
            expanded by apply_standardization().
    """
    df_expanded = expand_countries_and_disease_multilabel(df)
    df_expanded = standardize_countries(df_expanded)
    return df_expanded


def expand_countries_multilabel(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per country mentioned in the raw Country text - no collapsing
    threshold, unlike expand_multivalued_fields()'s '>=3 -> International'
    rule. A publication naming 5 countries contributes to all 5 (multi-label
    counting), matching the design of expand_algorithms_multilabel().

    Disease/Algorithm are left untouched: this view is for Figure 3 / 3b
    only, which have no disease/algorithm dimension, so it must not multiply
    rows - and inflate country counts - for publications that also mention
    several diseases/algorithms.
    """
    expanded_rows = []

    for idx, row in df.iterrows():
        countries = parse_field(row['Country'])
        if len(countries) == 0:
            countries = ['Unknown']

        for country in countries:
            new_row = row.copy()
            new_row['Country'] = country.strip()
            expanded_rows.append(new_row)

    return pd.DataFrame(expanded_rows).reset_index(drop=True)


def apply_country_standardization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Multi-label country standardization for Figure 3 / 3b (top countries).
    One row per (publication, country) mention.

    Args:
        df: Input DataFrame (filtered to Status='included'), not yet
            expanded by apply_standardization().
    """
    df_expanded = expand_countries_multilabel(df)
    df_expanded = standardize_countries(df_expanded)
    df_expanded = standardize_stages(df_expanded)
    return df_expanded


def expand_diseases_multilabel(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per disease category detected in the raw Disease text, via
    resolve_disease_categories() - see expand_algorithms_and_disease_multilabel
    for the 1-3-kept-separate / 4+-collapsed-to-'General' rule. Matches the
    design of expand_countries_multilabel() / expand_algorithms_multilabel().

    Country/Algorithm are left untouched: this view has no country/algorithm
    dimension, so it must not multiply rows for publications that also
    mention several countries/algorithms.
    """
    expanded_rows = []

    for idx, row in df.iterrows():
        for disease in resolve_disease_categories(row['Disease']):
            new_row = row.copy()
            new_row['Disease_standardized'] = disease
            expanded_rows.append(new_row)

    return pd.DataFrame(expanded_rows).reset_index(drop=True)


def apply_disease_standardization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Multi-label disease standardization - one row per (publication, disease)
    mention. Use this for narrative per-disease results (e.g. "how many
    publications addressed ASF"), where a publication studying 2-3 diseases
    should count toward each of them, consistent with how algorithms and
    countries are counted (apply_algorithm_standardization,
    apply_country_standardization). Table S2 / apply_publication_level_
    standardization() answer a related but different question - a single
    display string per publication (also multi-category-joined when a
    publication names 2-3 diseases, but still one row) - so mention counts
    here and publication counts there will not sum to the same total.

    Args:
        df: Input DataFrame (filtered to Status='included'), not yet
            expanded by apply_standardization().
    """
    df_expanded = expand_diseases_multilabel(df)
    df_expanded = standardize_stages(df_expanded)

    with_diseases = df['Disease'].notna().sum()
    print(f"\n  [multi-label] Publications with a disease listed: {with_diseases}")
    print(f"  [multi-label] Disease mentions counted: {len(df_expanded)}")

    return df_expanded


def standardize_diseases(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize disease values using map_disease_display (legacy
    apply_standardization() QA pathway only - see its docstring)."""
    df_copy = df.copy()
    df_copy['Disease_standardized'] = df_copy['Disease'].apply(map_disease_display)
    return df_copy


def standardize_countries(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize country values using map_country function."""
    df_copy = df.copy()
    df_copy['Country_standardized'] = df_copy['Country'].apply(map_country)
    return df_copy


def standardize_algorithms(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize algorithm values using map_algorithm_display (see
    apply_publication_level_standardization for why this is multi-label)."""
    df_copy = df.copy()
    df_copy['Algorithm_standardized'] = df_copy['Algorithm(s)'].apply(map_algorithm_display)
    return df_copy


def standardize_stages(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize stage values using map_stage function."""
    df_copy = df.copy()
    df_copy['Stage_standardized'] = df_copy['Stage'].apply(map_stage)
    return df_copy


def apply_standardization(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Full standardization pipeline:
    1. Expand multi-value fields
    2. Map to standard categories
    3. FILTER OUT Methodology/Review from algorithm statistics
    
    Args:
        df: Input DataFrame (filtered to Status='included')
        
    Returns:
        Tuple of (standardized_df, statistics_dict)
    """
    print("\n" + "="*80)
    print("STANDARDIZATION PIPELINE")
    print("="*80)
    
    # Step 1: Expand multi-value fields
    print("\n[1/5] Expanding multi-valued fields...")
    initial_rows = len(df)
    df_expanded = expand_multivalued_fields(df)
    expanded_rows = len(df_expanded)
    print(f"  Before expansion: {initial_rows} records")
    print(f"  After expansion: {expanded_rows} records")
    print(f"  New rows created: {expanded_rows - initial_rows}")
    
    # Step 2: Standardize diseases
    print("\n[2/5] Standardizing diseases...")
    df_expanded = standardize_diseases(df_expanded)
    disease_counts = df_expanded['Disease_standardized'].value_counts()
    print(f"  Standardized to {len(disease_counts)} categories:")
    for disease, count in disease_counts.head(10).items():
        pct = (count / len(df_expanded)) * 100
        print(f"    {disease:20s}: {count:3d} ({pct:5.1f}%)")
    
    # Step 3: Standardize countries
    print("\n[3/5] Standardizing countries...")
    df_expanded = standardize_countries(df_expanded)
    country_counts = df_expanded['Country_standardized'].value_counts()
    print(f"  Standardized to {len(country_counts)} categories:")
    for country, count in country_counts.head(10).items():
        pct = (count / len(df_expanded)) * 100
        print(f"    {country:25s}: {count:3d} ({pct:5.1f}%)")
    
    # Step 4: Standardize stages PRZED algorytmami
    print("\n[4/5] Standardizing stages...")
    df_expanded = standardize_stages(df_expanded)
    stage_counts = df_expanded['Stage_standardized'].value_counts()
    print(f"  Standardized to {len(stage_counts)} categories:")
    for stage, count in stage_counts.items():
        pct = (count / len(df_expanded)) * 100
        print(f"    {stage:25s}: {count:3d} ({pct:5.1f}%)")
    
    # Step 5: Standardize algorithms
    print("\n[5/5] Standardizing algorithms...")
    df_expanded = standardize_algorithms(df_expanded)

    # FILTRUJ REVIEW/METHODOLOGY i None (review, SHAP, non-ML) - nie bierz ich do statystyk
    df_algo_only = df_expanded[df_expanded['Stage_standardized'] != 'Methodology/Review'].copy()
    df_algo_only = df_algo_only[df_algo_only['Algorithm_standardized'].notna()].copy()
    algo_counts = df_algo_only['Algorithm_standardized'].value_counts()

    print(f"  Standardized to {len(algo_counts)} categories (excluding Methodology/Review):")
    print(f"  Total records for algo stats: {len(df_algo_only)} (excluded: {len(df_expanded) - len(df_algo_only)})")
    for algo, count in algo_counts.items():
        pct = (count / len(df_algo_only)) * 100
        print(f"    {algo:25s}: {count:3d} ({pct:5.1f}%)")

    # Create clean working dataframe (zachowaj wszystkie, ale statystyki bez review)
    df_clean = df_expanded[[
        'Authors', 'Year', 'Title', 'DOI', 'Journal',
        'Disease', 'Disease_standardized',
        'Country', 'Country_standardized',
        'Algorithm(s)', 'Algorithm_standardized',
        'Stage', 'Stage_standardized',
        'Section', 'Main metric', 'Notes', 'Sources'
    ]].copy()
    
    # Prepare statistics (TYLKO dla non-review)
    stats = {
        'original_records': initial_rows,
        'expanded_records': expanded_rows,
        'records_for_algorithm_stats': len(df_algo_only),
        'excluded_methodology_review': len(df_expanded) - len(df_algo_only),
        'unique_diseases': disease_counts.to_dict(),
        'unique_countries': country_counts.to_dict(),
        'unique_algorithms': algo_counts.to_dict(),  # Tylko empirical!
        'unique_stages': stage_counts.to_dict(),
    }
    
    print("\n" + "="*80)
    print("✓ Standardization complete")
    print("="*80)
    
    return df_clean, stats


if __name__ == "__main__":
    from src.data_cleaning import load_data, remove_excluded

    data_path = Path("data/data_ml_publications.xlsx")
    df = load_data(data_path)
    df_clean = remove_excluded(df)
    
    df_standardized, stats = apply_standardization(df_clean)
    
    print("\n\nPreview of standardized data:")
    print(df_standardized[['Disease', 'Disease_standardized', 'Country', 'Country_standardized', 'Algorithm(s)', 'Algorithm_standardized']].head(20))