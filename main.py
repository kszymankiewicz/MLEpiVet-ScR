"""
MLEpiVet-ScR - main execution script for PRISMA-ScR scoping review data analysis.
Application of Machine Learning Methods in the Epidemiology of Notifiable Animal Diseases
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so the local `src` package can be imported
# regardless of the working directory main.py is invoked from.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loading import load_data, print_qa_summary, qa_report
from src.fig_algorithms import figure_2_methods
from src.fig_disease_context import figure_5_disease_context
from src.fig_diseases import figure_4_disease_heatmap
from src.fig_geography import figure_3_geography
from src.fig_performance import figure_6_performance
from src.fig_trend import figure_1_temporal_trend
from src.tables import save_qa_report, save_table_s1

VERSION = '2.0.0'


def parse_args():
    parser = argparse.ArgumentParser(description='MLEpiVet-ScR analysis pipeline')
    parser.add_argument('--data', type=Path, default=Path('data/data_final.xlsx'),
                        help='extraction sheet (default: data/data_final.xlsx)')
    parser.add_argument('--figures', type=Path, default=Path('figures'),
                        help='output folder for figures (default: figures/)')
    parser.add_argument('--output', type=Path, default=Path('output'),
                        help='output folder for tables (default: output/)')
    return parser.parse_args()


def main():
    args = parse_args()
    print('=' * 80)
    print(f'MLEpiVet-ScR v{VERSION} - PRISMA-ScR Scoping Review Data Analysis Pipeline')
    print('=' * 80)
    args.figures.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)

    print('\n[1/4] Loading and standardising data...')
    df = load_data(args.data)
    print(f'    {len(df)} publications ({int(df["is_review"].sum())} reviews)')

    print('\n[2/4] Mapping QA...')
    sheets = qa_report(df)
    print_qa_summary(sheets)
    save_qa_report(sheets, args.output / 'mapping_review.xlsx')

    print('\n[3/4] Table S1...')
    save_table_s1(df, args.output / 'Table_S1_included_studies.xlsx')

    print('\n[4/4] Figures...')
    for make_figure in (figure_1_temporal_trend, figure_2_methods, figure_3_geography,
                        figure_4_disease_heatmap, figure_5_disease_context,
                        figure_6_performance):
        make_figure(df, args.figures)

    print('\n' + '=' * 80)
    print('Pipeline complete!')
    print('=' * 80)


if __name__ == '__main__':
    main()
