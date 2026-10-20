"""
Figure 6: reported model performance and reporting quality.

  A - AUC (AUC/AUROC) range per publication (worst to best reported model)
  B - accuracy range per publication
  C - reporting checklist (only when the optional reporting columns exist)

One row per publication, sorted by the best reported value. Colour shows
the validation scheme when the optional 'Validation' column is filled in,
otherwise the application stage. Values are as reported by the authors and
are not comparable across studies. Review articles are excluded.

Optional columns (coding rules in template/README.md):
  Validation           Random split/CV | Spatial | Temporal | External | None reported
  Reports_AUPRC        yes | no | NA
  Reports_SensSpec     yes | no | NA
  Reports_CI           yes | no | NA
  Reports_Calibration  yes | no | NA
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from src.plot_style import EDGE_COLOR, TEXT_COLOR, apply_style, panel_label, save_figure

STAGE_COLORS = {
    'Prediction/Forecasting': '#7FBFDC',
    'Surveillance': '#8CCF8A',
    'Diagnostics': '#F08A80',
    'Other': '#B5B5B5',
    'Field': '#C792C7',
}

VALIDATION_COLORS = {
    'Random split/CV': '#B5B5B5',
    'Spatial': '#7FBFDC',
    'Temporal': '#8CCF8A',
    'External': '#F08A80',
    'None reported': '#FFFFFF',
}

REPORTING_ITEMS = {
    'Reports_AUPRC': 'AUPRC',
    'Reports_SensSpec': 'Sensitivity & specificity',
    'Reports_CI': 'Confidence intervals',
    'Reports_Calibration': 'Calibration',
}

# Conventional AUC interpretation thresholds (Hosmer & Lemeshow).
AUC_REFERENCES = [(0.7, 'acceptable'), (0.8, 'excellent'), (0.9, 'outstanding')]


def _short_label(row) -> str:
    first_author = str(row['Authors']).split(',')[0].split()[0]
    return f"{first_author} {row['Year']}"


def _range_panel(ax, data: pd.DataFrame, xlabel: str, color_of, references=()) -> None:
    data = data.sort_values(['metric_max', 'metric_min'], ascending=False).reset_index(drop=True)
    y = np.arange(len(data))
    for ref, label in references:
        ax.axvline(ref, color='#CCCCCC', lw=0.6, ls='--', zorder=0)
        ax.text(ref - 0.006, -0.9, label, ha='right', va='bottom', fontsize=5.5,
                color='#888888', style='italic', rotation=90)
    for yi, row in data.iterrows():
        color = color_of(row)
        lo = row['metric_min'] if pd.notna(row['metric_min']) else row['metric_max']
        line_color = '#DDDDDD' if color == '#FFFFFF' else color
        ax.hlines(yi, lo, row['metric_max'], color=line_color, lw=2.2, alpha=0.7, zorder=1)
        if lo != row['metric_max']:
            ax.scatter(lo, yi, s=14, facecolor='white', edgecolor=EDGE_COLOR, lw=0.5, zorder=2)
        ax.scatter(row['metric_max'], yi, s=22, color=color, edgecolor=EDGE_COLOR, lw=0.5, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(data['label'], fontsize=6)
    ax.set_ylim(len(data) - 0.4, -1.6 if not references else -4.2)
    ax.set_xlabel(xlabel, fontweight='bold')
    ax.grid(axis='x', color='#F0F0F0', lw=0.5)
    ax.set_axisbelow(True)
    ax.set_title(f'n = {len(data)}; median best = {data["metric_max"].median():.2f}',
                 fontsize=7, color='#555555', loc='left')


def _reporting_panel(ax, data: pd.DataFrame) -> None:
    """Share of publications (with a performance metric) reporting each item."""
    items = []
    for col, label in REPORTING_ITEMS.items():
        if col in data.columns:
            # 'NA' (not applicable) is excluded from the denominator.
            coded = data[col].astype(str).str.lower()
            applicable = coded.isin(['yes', 'no'])
            if applicable.any():
                items.append((label, coded[applicable].eq('yes').mean()))
    validation = data['Validation'].dropna().value_counts(normalize=True)
    items += [(f'Validation: {v}', validation.get(v, 0.0))
              for v in VALIDATION_COLORS if v != 'Random split/CV']
    y = np.arange(len(items))
    ax.barh(y, [share * 100 for _, share in items], color='#A8D8EA', edgecolor=EDGE_COLOR,
            linewidth=0.5, height=0.65)
    for yi, (_, share) in zip(y, items):
        ax.text(share * 100 + 1.5, yi, f'{share:.0%}', va='center', fontsize=6.5,
                color=TEXT_COLOR)
    ax.set_yticks(y)
    ax.set_yticklabels([label for label, _ in items], fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel('% of publications', fontweight='bold')


def figure_6_performance(df: pd.DataFrame, output_dir: Path) -> None:
    apply_style()
    data = df[~df['is_review'] & df['metric_max'].notna()].copy()
    # "Author Year", with a/b suffixes where two publications share a label.
    data['label'] = data.apply(_short_label, axis=1)
    dup = data['label'].duplicated(keep=False)
    data.loc[dup, 'label'] += data[dup].groupby('label').cumcount().map(lambda i: 'ab'[i])
    auc = data[data['metric_type'] == 'AUC']
    acc = data[data['metric_type'] == 'Accuracy']

    has_validation = 'Validation' in data.columns and data['Validation'].notna().any()
    if has_validation:
        palette, key, title = VALIDATION_COLORS, 'Validation', 'Validation scheme'
    else:
        palette, key, title = STAGE_COLORS, 'Stage', 'Stage'
    color_of = lambda row: palette.get(row[key], '#B5B5B5')

    fig = plt.figure(figsize=(7.2, 7.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1],
                          height_ratios=[len(acc) + 4, max(len(auc) - len(acc), 8)],
                          wspace=0.45, hspace=0.25)
    ax_a = fig.add_subplot(gs[:, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    bottom = gs[1, 1].subgridspec(2, 1, height_ratios=[0.45, 0.55], hspace=0.5)
    ax_leg = fig.add_subplot(bottom[0])
    ax_leg.axis('off')

    _range_panel(ax_a, auc, 'Reported AUC', color_of, AUC_REFERENCES)
    ax_a.set_xlim(0.38, 1.02)
    _range_panel(ax_b, acc, 'Reported accuracy', color_of)
    ax_b.set_xlim(0.38, 1.02)
    panel_label(ax_a, 'A', x=-0.25, y=1.01)
    panel_label(ax_b, 'B', x=-0.25, y=1.03)

    if has_validation:
        ax_c = fig.add_subplot(bottom[1])
        _reporting_panel(ax_c, data)
        panel_label(ax_c, 'C', x=-0.62, y=1.12)

    shown = [v for v in palette if v in set(auc[key]) | set(acc[key])]
    handles = [Line2D([], [], color=palette[v] if palette[v] != '#FFFFFF' else '#DDDDDD', lw=2.2,
                      marker='o', markersize=5, markerfacecolor=palette[v],
                      markeredgecolor=EDGE_COLOR, markeredgewidth=0.5, label=v) for v in shown]
    handles += [Line2D([], [], lw=0, marker='o', markersize=5, markerfacecolor='#999999',
                       markeredgecolor=EDGE_COLOR, label='Best reported model'),
                Line2D([], [], lw=0, marker='o', markersize=4, markerfacecolor='white',
                       markeredgecolor=EDGE_COLOR, label='Worst reported model')]
    ax_leg.legend(handles=handles, loc='upper left', fontsize=7, frameon=False,
                  title=title, title_fontsize=7.5, alignment='left',
                  ncol=1 if not has_validation else 2)

    print('Figure 6: reported performance')
    print(f'  AUC: n = {len(auc)}, best >= 0.9: {(auc["metric_max"] >= 0.9).sum()}, '
          f'median best {auc["metric_max"].median():.3f}')
    print(f'  Accuracy: n = {len(acc)}, best >= 0.9: {(acc["metric_max"] >= 0.9).sum()}')
    if not has_validation:
        print('  Validation/reporting columns not found - panel C skipped, colour = Stage')
    save_figure(fig, output_dir, 'Figure_6_reported_performance')
