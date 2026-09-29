"""
Main execution script for PRISMA-ScR scoping review data analysis.
Application of Machine Learning Methods in the Epidemiology of Notifiable Animal Diseases
"""

from pathlib import Path
import sys

# Ensure project root is on sys.path so the local `src` package can be imported
# regardless of the working directory main.py is invoked from.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_cleaning import load_data, remove_excluded
from src.standardization import (
    apply_standardization,
    apply_publication_level_standardization,
    apply_algorithm_standardization,
    apply_algorithm_disease_standardization,
    apply_country_standardization,
    apply_country_disease_standardization,
    apply_disease_standardization,
    verify_algorithm_consistency,
)
from src.figure_generator import generate_all_figures
from src.table_generator import generate_table_s2, save_standardized_preview
from src.disease_summary import build_disease_summary, save_disease_summary


def main():
    print("="*80)
    print("PRISMA-ScR Scoping Review - Data Analysis Pipeline")
    print("="*80)

    # Paths
    data_path = Path("data/data_ml_publications.xlsx")
    output_dir = Path("output")
    figures_dir = Path("figures")

    output_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    # Step 1: Load data
    print("\n[1/6] Loading data...")
    df = load_data(data_path)
    df = remove_excluded(df)
    print(f"    Loaded {len(df)} records (excluded removed)")

    # Step 2: Generate Table S2 (one row per publication)
    print("\n[2/6] Generating Table S2 (complete bibliography)...")
    table_s2_path = output_dir / "Table_S2_Complete_Bibliography.xlsx"
    generate_table_s2(df, table_s2_path)
    print(f"    Table S2 saved to {table_s2_path}")

    # Step 3: Standardize data
    print("\n[3/6] Standardizing data...")
    # Publication-level (one row per publication) - used for Figure 1, Figure 5
    df_pub_standardized = apply_publication_level_standardization(df)
    # Disease x country expanded (QA/reference only - not used by any figure,
    # since Year/Stage would get silently duplicated across the expansion)
    df_standardized, stats = apply_standardization(df)
    print(f"    Standardization complete: {len(df_standardized)} rows after expansion")
    df_algo_disease_standardized = apply_algorithm_disease_standardization(df)
    df_algo_standardized = apply_algorithm_standardization(df)
    df_country_standardized = apply_country_standardization(df)
    df_country_disease_standardized = apply_country_disease_standardization(df)
    df_disease_standardized = apply_disease_standardization(df)

    mismatches = verify_algorithm_consistency(df_pub_standardized, df_algo_standardized)
    if mismatches:
        raise RuntimeError(
            f"Algorithm mapping inconsistency: Table S2 and Figure 2/4 disagree "
            f"on {mismatches} publication(s) - see [QA] log above."
        )

    # Step 4: Save a preview of the standardized data actually used to draw
    # the figures, for manual spot-checking of the mappings
    print("\n[4/6] Saving standardized data preview...")
    preview_path = output_dir / "standardized_data_preview.xlsx"
    save_standardized_preview({
        "Publication-level (Fig1,5)": df_pub_standardized,
        "Disease+Country expanded (QA only)": df_standardized,
        "Algorithm (Fig4)": df_algo_standardized,
        "Algorithm x Disease (Fig2)": df_algo_disease_standardized,
        "Country (Fig3, 3b)": df_country_standardized,
        "Country x Disease (summary table)": df_country_disease_standardized,
        "Disease multilabel (not for text)": df_disease_standardized,
    }, preview_path)
    print(f"    Preview saved to {preview_path}")

    # Step 5: Generate figures
    print("\n[5/6] Generating figures...")
    generate_all_figures(df_pub_standardized, df_algo_disease_standardized, df_algo_standardized,
                          df_country_standardized, figures_dir)
    print(f"    Figures saved to {figures_dir}/")

    # Step 6: Disease summary table (n, %, stage mix, top algorithms/countries,
    # year range per disease) - built from the same standardized dataframes above
    print("\n[6/6] Generating disease summary table...")
    disease_summary = build_disease_summary(df_pub_standardized, df_disease_standardized,
                                             df_algo_disease_standardized, df_country_disease_standardized)
    save_disease_summary(disease_summary, output_dir)

    print("\n" + "="*80)
    print("Pipeline complete!")
    print("="*80)

if __name__ == "__main__":
    main()
