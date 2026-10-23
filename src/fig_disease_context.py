"""
Figure 5: diseases by application stage and theme (bubble matrix).

Columns: WOAH-listed viral diseases in the host-group order of Figures 3B
and 4. Rows: Stage (top block) and Theme (bottom block). Bubble area is the
number of publications; small grey dots mark combinations with no
publication, which are the research gaps. Review articles are excluded.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.plot_style import (
    EDGE_COLOR, HOST_COLORS, TEXT_COLOR, apply_style, disease_groups, fit_text, save_figure,
)

BUBBLE_SCALE = 22  # marker area (pt^2) per publication
BLOCKS = [('Stage', 'Stage'), ('Theme', 'Theme')]


def figure_5_disease_context(df: pd.DataFrame, output_dir: Path) -> None:
    apply_style()
    data = df[~df['is_review']]
    disease_counts = data['disease_list'].explode().value_counts()
    groups = disease_groups(disease_counts)
    cols = [d for _, ds in groups for d in ds]
    host_of = {d: h for h, ds in groups for d in ds}

    rows, block_spans = [], []
    for title, column in BLOCKS:
        values = data[column].value_counts().index.tolist()
        block_spans.append((title, len(rows) + (1 if rows else 0), len(values)))
        if rows:
            rows.append(None)  # spacer
        rows.extend((column, v) for v in values)

    long = data[['disease_list', 'Stage', 'Theme']].explode('disease_list').dropna(
        subset=['disease_list']).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    for yi, row in enumerate(rows):
        if row is None:
            continue
        column, value = row
        counts = long.loc[long[column] == value, 'disease_list'].value_counts()
        for xi, d in enumerate(cols):
            n = int(counts.get(d, 0))
            if n:
                ax.scatter(xi, yi, s=n * BUBBLE_SCALE, color=HOST_COLORS[host_of[d]],
                           edgecolor=EDGE_COLOR, linewidth=0.5, zorder=3)
                if n >= 2:
                    ax.text(xi, yi, str(n), ha='center', va='center', fontsize=6,
                            color=TEXT_COLOR, zorder=4)
            else:
                ax.scatter(xi, yi, s=3, color='#CCCCCC', zorder=2)

    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([f'{d}\n({disease_counts[d]})' for d in cols], fontsize=7,
                       fontweight='bold', linespacing=1.1)
    ax.set_yticks([i for i, r in enumerate(rows) if r is not None])
    ax.set_yticklabels([r[1] for r in rows if r is not None], fontsize=7.5)
    ax.tick_params(length=0)
    ax.set_xlim(-0.6, len(cols) - 0.4)
    ax.set_ylim(len(rows) - 0.4, -1.6)
    for s in ax.spines.values():
        s.set_visible(False)

    for title, first, n in block_spans:
        ax.annotate(title, xy=(1, first + (n - 1) / 2), xycoords=('axes fraction', 'data'),
                    xytext=(8, 0), textcoords='offset points', rotation=270,
                    ha='center', va='center', fontsize=8, fontweight='bold')
    for i, r in enumerate(rows):
        if r is None:
            ax.axhline(i, color='#999999', lw=0.6)

    start = 0
    for i, (host, ds) in enumerate(groups):
        end = start + len(ds) - 1
        ax.add_patch(plt.Rectangle((start - 0.45, -1.5), end - start + 0.9, 0.8,
                                   color=HOST_COLORS[host], clip_on=False, zorder=1))
        fit_text(ax, (start + end) / 2, -1.1, end - start + 0.8, 0.72, host,
                 fontweight='bold', color=TEXT_COLOR)
        if i:
            ax.axvline(start - 0.5, color='#DDDDDD', lw=0.6, zorder=0)
        start = end + 1

    sizes = [1, 5, 10, 20]
    handles = [plt.scatter([], [], s=n * BUBBLE_SCALE, color='white', edgecolor=EDGE_COLOR,
                           linewidth=0.5, label=str(n)) for n in sizes]
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.1),
              ncol=len(sizes), fontsize=6.5, frameon=False, columnspacing=2.4,
              title='Number of publications', title_fontsize=7, borderpad=0.8)

    print('Figure 5: disease x stage / theme')
    for column in ('Stage', 'Theme'):
        empty = [(v, d) for v in data[column].unique() for d in cols
                 if not ((long[column] == v) & (long['disease_list'] == d)).any()]
        print(f'  Empty {column} x disease cells: {len(empty)} of '
              f'{data[column].nunique() * len(cols)}')
    save_figure(fig, output_dir, 'Figure_5_disease_stage_theme')
