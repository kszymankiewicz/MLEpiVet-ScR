"""
Figure 1: publications per year, stacked by algorithm category (F1).

Review articles are excluded. Stacked segments count category uses (a
publication with three categories adds to three segments), so bar height
can exceed the number of publications; the line shows publications per year.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from src.mappings import RARE_CATEGORIES
from src.plot_style import (
    EDGE_COLOR, TEXT_COLOR, apply_style, category_color, family_category_order,
    save_figure,
)

LAST_YEAR = 2026
PARTIAL_YEAR_NOTE = 'Search completed\nMay–June 2026'


def figure_1_temporal_trend(df: pd.DataFrame, output_dir: Path) -> None:
    apply_style()
    data = df[~df['is_review']]
    order = family_category_order(data)
    categories = [c for _, _, cats in order for c, _ in cats]

    years = np.arange(int(data['Year'].min()), LAST_YEAR + 1)
    long = data[['Year', 'F1']].explode('F1').reset_index(drop=True)
    uses = (pd.crosstab(long['Year'], long['F1'])
            .reindex(index=years, columns=categories, fill_value=0))
    pubs = data['Year'].value_counts().reindex(years, fill_value=0)

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bottom = np.zeros(len(years))
    for category in categories:
        values = uses[category].to_numpy()
        bars = ax.bar(years, values, bottom=bottom, width=0.75,
                      color=category_color(category), edgecolor='white', linewidth=0.5)
        if years[-1] == LAST_YEAR:
            bars[-1].set_hatch('////')
            bars[-1].set_edgecolor('white')
        bottom += values

    ax.plot(years, pubs.to_numpy(), color=TEXT_COLOR, marker='o', markersize=4,
            linewidth=1.4, zorder=3)
    for x, n in zip(years, pubs.to_numpy()):
        ax.annotate(str(n), xy=(x, n), xytext=(0, 5), textcoords='offset points',
                    ha='center', va='bottom', fontsize=7, fontweight='bold', color=TEXT_COLOR,
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none',
                              alpha=0.85), zorder=4)

    ax.text(LAST_YEAR + 0.1, bottom[-1] + 6.0, PARTIAL_YEAR_NOTE, ha='center', va='bottom',
            fontsize=6.5, color='#666666', style='italic')

    ax.set_xticks(years)
    ax.set_xticklabels(years, fontsize=7.5)
    ax.set_xlim(years[0] - 0.6, years[-1] + 0.6)
    ax.set_ylim(0, bottom.max() * 1.3)
    ax.set_xlabel('Publication year', fontweight='bold')
    ax.set_ylabel('Number of category uses / publications', fontweight='bold')
    ax.grid(axis='y', color='#EEEEEE', lw=0.5)
    ax.set_axisbelow(True)

    main = [c for c in categories if c not in RARE_CATEGORIES]
    rare = [c for c in categories if c in RARE_CATEGORIES]
    handles = [Patch(facecolor=category_color(c), edgecolor=EDGE_COLOR, linewidth=0.4, label=c)
               for c in main]
    if rare:
        handles.append(Patch(facecolor=category_color(rare[0]), edgecolor=EDGE_COLOR,
                             linewidth=0.4, label='Other (' + ', '.join(rare) + ')'))
    handles.append(Line2D([], [], color=TEXT_COLOR, marker='o', markersize=4, lw=1.4,
                          label='Publications'))
    ax.legend(handles=handles, loc='upper left', ncol=3, fontsize=6.5, frameon=False,
              handlelength=1.2, columnspacing=1.0)

    print('Figure 1: temporal trend by algorithm category')
    print(f'  Publications (reviews excluded): {len(data)}; years {years[0]}-{years[-1]}')
    first_use = long.groupby('F1')['Year'].min().reindex(categories)
    print('  First year per category: ' + ', '.join(f'{c} {y}' for c, y in first_use.items()))
    save_figure(fig, output_dir, 'Figure_1_temporal_trend')
