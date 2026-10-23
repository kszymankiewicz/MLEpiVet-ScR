"""
Figure 4: algorithm categories (F1) x WOAH-listed viral diseases.

Columns are grouped by main host (same order and colours as Figure 3B) and
labelled with the number of publications per disease; rows follow the
method-family order of Figure 2. Review articles are excluded; a
publication counts once in every category x disease cell it belongs to.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.fig_algorithms import HEATMAP_CMAP
from src.plot_style import (
    HOST_COLORS, TEXT_COLOR, apply_style, category_color, disease_groups,
    family_category_order, fit_text, save_figure,
)


def figure_4_disease_heatmap(df: pd.DataFrame, output_dir: Path) -> None:
    apply_style()
    data = df[~df['is_review']]
    order = family_category_order(data)
    rows = [c for _, _, cats in order for c, _ in cats]

    disease_counts = data['disease_list'].explode().value_counts()
    groups = disease_groups(disease_counts)
    cols = [d for _, ds in groups for d in ds]

    long = (data[['F1', 'disease_list']].explode('F1').explode('disease_list')
            .dropna().reset_index(drop=True))
    table = (pd.crosstab(long['F1'], long['disease_list'])
             .reindex(index=rows, columns=cols, fill_value=0))

    fig = plt.figure(figsize=(7.2, 4.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 0.025], wspace=0.03)
    ax = fig.add_subplot(gs[0])
    cax = fig.add_subplot(gs[1])

    im = ax.imshow(table.values, cmap=HEATMAP_CMAP, aspect='auto', vmin=0)
    vmax = table.values.max()
    for (i, j), v in np.ndenumerate(table.values):
        if v:
            ax.text(j, i, v, ha='center', va='center', fontsize=6.5,
                    color='white' if v > vmax * 0.6 else TEXT_COLOR)

    x = np.arange(len(cols))
    ax.set_xticks(x)
    ax.set_xticklabels([f'{d}\n({disease_counts[d]})' for d in cols], fontsize=7,
                       linespacing=1.1)
    for tick in ax.get_xticklabels():
        tick.set_fontweight('bold')
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=7.5)
    for tick, category in zip(ax.get_yticklabels(), rows):
        tick.set_bbox(dict(facecolor=category_color(category), edgecolor='none', pad=1.2))
    ax.set_xticks(np.arange(-0.5, len(cols)), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows)), minor=True)
    ax.grid(which='minor', color='white', lw=1.0)
    ax.tick_params(which='both', length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    boundary = 0
    for _, _, cats in order[:-1]:
        boundary += len(cats)
        ax.axhline(boundary - 0.5, color='#777777', lw=0.8)

    # Host-group bands above the columns, coloured as in Figure 3B.
    start = 0
    for i, (host, ds) in enumerate(groups):
        end = start + len(ds) - 1
        ax.add_patch(plt.Rectangle((start - 0.45, -1.45), end - start + 0.9, 0.8,
                                   color=HOST_COLORS[host], clip_on=False))
        fit_text(ax, (start + end) / 2, -1.05, end - start + 0.8, 0.72, host,
                 fontweight='bold', color=TEXT_COLOR, clip_on=False)
        if i:
            ax.axvline(start - 0.5, color='#777777', lw=0.8)
        start = end + 1
    ax.set_ylim(len(rows) - 0.5, -0.5)

    cb = fig.colorbar(im, cax=cax)
    cb.set_label('Number of publications', fontsize=7)
    cb.ax.tick_params(labelsize=6.5)
    cb.outline.set_visible(False)

    print('Figure 4: algorithm category x disease')
    print(f'  Publications (reviews excluded): {len(data)}; diseases shown: {len(cols)}')
    save_figure(fig, output_dir, 'Figure_4_disease_heatmap')
