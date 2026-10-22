"""
Figure S2: co-occurrence of algorithm categories (F1).

Off-diagonal cells: publications using both categories. Diagonal (framed):
publications using that category alone. Rows and columns follow the
method-family order of Figure 2. Review articles are excluded.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.fig_algorithms import HEATMAP_CMAP
from src.plot_style import (
    TEXT_COLOR, apply_style, category_color, family_category_order, save_figure,
)


def cooccurrence_matrix(df: pd.DataFrame, categories: list) -> np.ndarray:
    m = np.zeros((len(categories), len(categories)), dtype=int)
    for cats in df['F1']:
        idx = [categories.index(c) for c in cats]
        if len(idx) == 1:
            m[idx[0], idx[0]] += 1
        for i in idx:
            for j in idx:
                if i != j:
                    m[i, j] += 1
    return m


def figure_s2_cooccurrence(df: pd.DataFrame, output_dir: Path) -> None:
    apply_style()
    data = df[~df['is_review']]
    order = family_category_order(data)
    cats = [c for _, _, cs in order for c, _ in cs]
    m = cooccurrence_matrix(data, cats)
    n = len(cats)

    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    im = ax.imshow(np.ma.array(m, mask=np.triu(np.ones_like(m, bool), 1)),
                   cmap=HEATMAP_CMAP, vmin=0)
    vmax = m.max()
    for i in range(n):
        for j in range(i + 1):
            if m[i, j]:
                ax.text(j, i, m[i, j], ha='center', va='center', fontsize=7,
                        fontweight='bold' if i == j else 'normal',
                        color='white' if m[i, j] > vmax * 0.6 else TEXT_COLOR)
        ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False,
                                   edgecolor='#555555', lw=0.8))

    ax.set_xticks(range(n))
    ax.set_xticklabels(cats, rotation=60, ha='right', rotation_mode='anchor', fontsize=7)
    ax.set_yticks(range(n))
    ax.set_yticklabels(cats, fontsize=7)
    for ticks in (ax.get_xticklabels(), ax.get_yticklabels()):
        for tick, category in zip(ticks, cats):
            tick.set_bbox(dict(facecolor=category_color(category), edgecolor='none', pad=1.0))
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title('Off-diagonal: publications using both categories\n'
                 'Diagonal (framed): publications using this category alone',
                 fontsize=7.5, loc='left', color='#555555')

    cb = fig.colorbar(im, ax=ax, shrink=0.6)
    cb.set_label('Number of publications', fontsize=7)
    cb.ax.tick_params(labelsize=6.5)
    cb.outline.set_visible(False)

    print('Figure S2: co-occurrence of algorithm categories')
    print(f'  Publications using a single category: {int(np.trace(m))} of {len(data)}')
    save_figure(fig, output_dir, 'Figure_S2_category_cooccurrence')
