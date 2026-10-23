"""
Figure 2: machine-learning methods.

  A - publications per algorithm category (F1), grouped by method family
  B - individual algorithms (F2) used in >= 2 publications, coloured by F1
  C - algorithm category (F1) x modelling target (grouped) heatmap

Review articles are excluded. The counting unit throughout is the
publication: a publication counts once for every category and algorithm it
uses, so bars and cells do not sum to the number of studies.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from src.mappings import ALGORITHM_CATEGORY, TARGET_GROUP_ORDER
from src.plot_style import (
    EDGE_COLOR, GRID_COLOR, TEXT_COLOR, apply_style, category_color,
    family_category_order, panel_label, save_figure,
)

MIN_PUBLICATIONS_F2 = 2

HEATMAP_CMAP = LinearSegmentedColormap.from_list('pastel_blue', ['#FFFFFF', '#A8D8EA', '#2C7FB8'])


FAMILY_LABELS = {
    'Classical supervised learning': 'Classical supervised\nlearning',
    'Neural networks and deep learning': 'Neural networks &\ndeep learning',
    'Domain-specific methods': 'Domain-specific\nmethods',
    'Unsupervised learning': 'Unsupervised\nlearning',
    'Probabilistic models': 'Probabilistic\nmodels',
}


def _wrap_family(name: str) -> str:
    return FAMILY_LABELS.get(name, name)


def panel_a_categories(ax, order) -> None:
    """Grouped bars: categories side by side within each method family."""
    x = 0.0
    for family, n_family, cats in order:
        start = x
        for category, n in cats:
            ax.bar(x, n, width=0.8, color=category_color(category),
                   edgecolor=EDGE_COLOR, linewidth=0.6)
            ax.text(x, n + 1.0, str(n), ha='center', va='bottom',
                    fontsize=6.5, color=TEXT_COLOR)
            ax.text(x, -2, category, ha='right', va='top', rotation=40,
                    rotation_mode='anchor', fontsize=7)
            x += 1
        mid = (start + x - 1) / 2
        ax.plot([start - 0.4, x - 0.6], [-27, -27], color='#888888', lw=0.8, clip_on=False)
        ax.text(mid, -29, f'{_wrap_family(family)}\n(n = {n_family})', ha='center',
                va='top', fontsize=7, fontweight='bold')
        x += 1.0
    ax.set_xlim(-0.7, x - 0.7)
    ax.set_ylim(0, max(n for _, _, cats in order for _, n in cats) * 1.12)
    ax.set_xticks([])
    ax.set_ylabel('Number of publications', fontweight='bold')


def panel_b_algorithms(ax, df: pd.DataFrame, order) -> None:
    """Lollipop chart of F2 algorithms, grouped by family then category."""
    counts = df['F2'].explode().value_counts()
    # Small datasets (e.g. the template) may have no algorithm used twice.
    min_n = MIN_PUBLICATIONS_F2 if (counts >= MIN_PUBLICATIONS_F2).any() else 1
    rows, family_spans = [], []
    for family, _, cats in order:
        first = len(rows)
        for category, _ in cats:
            algs = counts[[ALGORITHM_CATEGORY[a] == category for a in counts.index]]
            algs = algs[algs >= min_n]
            rows.extend((alg, int(n), category) for alg, n in algs.items())
        if len(rows) > first:
            family_spans.append((family, first, len(rows) - 1))

    y = np.arange(len(rows))
    xpad = max(r[1] for r in rows) * 0.035
    for yi, (alg, n, category) in zip(y, rows):
        ax.hlines(yi, 0, n, color='#BBBBBB', lw=1.0, zorder=1)
        ax.scatter(n, yi, s=38, color=category_color(category), edgecolor=EDGE_COLOR,
                   linewidth=0.6, zorder=2)
        ax.text(n + xpad, yi, str(n), va='center', fontsize=6.5, color=TEXT_COLOR)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=7)
    ax.set_ylim(len(rows) - 0.4, -0.6)
    xmax = max(r[1] for r in rows)
    ax.set_xlim(0, xmax * 1.12)
    ax.set_xlabel('Number of publications', fontweight='bold')
    ax.grid(axis='x', color=GRID_COLOR, lw=0.5)
    ax.set_axisbelow(True)

    for i, (family, first, last) in enumerate(family_spans):
        if i:
            ax.axhline(first - 0.5, color='#999999', lw=0.6, ls='--')
        ax.text(xmax * 1.11, (first + last) / 2, _wrap_family(family), ha='right',
                va='center', fontsize=6.5, color='#777777', style='italic')


HEATMAP_BLOCKS = [('Modelling target', 'target_group')]
ROW_ORDERS = {'target_group': TARGET_GROUP_ORDER}


def _category_crosstab(df: pd.DataFrame, column: str, col_order: list) -> pd.DataFrame:
    long = df[['F1', column]].explode('F1').explode(column).reset_index(drop=True)
    table = pd.crosstab(long[column], long['F1'])
    present = df[column].explode().value_counts().index.tolist()
    row_order = [r for r in ROW_ORDERS.get(column, present) if r in present]
    return table.reindex(index=row_order, columns=col_order, fill_value=0)


def panel_c_heatmap(ax, df: pd.DataFrame, order, cbar_ax, blocks=HEATMAP_BLOCKS) -> None:
    """Publications per row block (e.g. target group) x F1 category (columns)."""
    col_order = [c for _, _, cats in order for c, _ in cats]
    blocks = [(title, _category_crosstab(df, column, col_order))
              for title, column in blocks]

    # Stack blocks with one empty spacer row between them.
    spacer = pd.DataFrame(np.nan, index=[''], columns=col_order)
    parts, block_spans, row = [], [], 0
    for i, (title, table) in enumerate(blocks):
        if i:
            parts.append(spacer)
            row += 1
        parts.append(table)
        block_spans.append((title, row, row + len(table) - 1))
        row += len(table)
    stacked = pd.concat(parts)
    values = np.ma.masked_invalid(stacked.values.astype(float))

    im = ax.imshow(values, cmap=HEATMAP_CMAP, aspect='auto', vmin=0)
    vmax = np.nanmax(stacked.values.astype(float))
    for (i, j), v in np.ndenumerate(stacked.values.astype(float)):
        if v and not np.isnan(v):
            ax.text(j, i, int(v), ha='center', va='center', fontsize=6.5,
                    color='white' if v > vmax * 0.6 else TEXT_COLOR)

    ax.xaxis.tick_top()
    ax.set_xticks(range(len(col_order)))
    ax.set_xticklabels(col_order, rotation=60, ha='left', rotation_mode='anchor', fontsize=7)
    for tick, category in zip(ax.get_xticklabels(), col_order):
        tick.set_bbox(dict(facecolor=category_color(category), edgecolor='none', pad=1.2))
    ax.set_yticks(range(len(stacked)))
    ax.set_yticklabels(stacked.index, fontsize=7)
    ax.tick_params(which='both', length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    # White cell borders, drawn per block so the spacer row stays blank.
    for _, first, last in block_spans:
        for r in range(first, last + 2):
            ax.hlines(r - 0.5, -0.5, len(col_order) - 0.5, color='white', lw=1.0)
        ax.vlines(np.arange(-0.5, len(col_order)), first - 0.5, last + 0.5, color='white', lw=1.0)
        boundary = 0
        for _, _, cats in order[:-1]:
            boundary += len(cats)
            ax.vlines(boundary - 0.5, first - 0.5, last + 0.5, color='#777777', lw=0.8)

    for title, first, last in block_spans:
        ax.annotate(title, xy=(1, (first + last) / 2), xycoords=('axes fraction', 'data'),
                    xytext=(8, 0), textcoords='offset points', rotation=270,
                    ha='center', va='center', fontsize=8, fontweight='bold')

    cb = ax.figure.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cb.set_ticks(np.arange(0, vmax + 1, 5))
    cb.set_label('Number of publications', fontsize=7)
    cb.ax.tick_params(labelsize=6.5)
    cb.outline.set_visible(False)


def figure_2_methods(df: pd.DataFrame, output_dir: Path, blocks=HEATMAP_BLOCKS,
                     name: str = 'Figure_2_ml_methods') -> None:
    apply_style()
    data = df[~df['is_review']]
    order = family_category_order(data)

    fig = plt.figure(figsize=(7.2, 10.8))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.75, 1.6], width_ratios=[0.85, 1.15],
                          hspace=0.45, wspace=1.05)
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    sub = gs[1, 1].subgridspec(3, 1, height_ratios=[0.30, 0.38, 0.32], hspace=0.05)
    ax_c = fig.add_subplot(sub[1, 0])
    # Colour bar spans the full width of the heatmap.
    cb_gs = sub[2, 0].subgridspec(3, 1, height_ratios=[0.1, 0.1, 0.8])
    ax_cb = fig.add_subplot(cb_gs[1, 0])

    panel_a_categories(ax_a, order)
    panel_b_algorithms(ax_b, data, order)
    panel_c_heatmap(ax_c, data, order, ax_cb, blocks)
    panel_label(ax_a, 'A')
    panel_label(ax_b, 'B')
    panel_label(ax_c, 'C', x=-0.62, y=1.02)

    n_f2 = data['F2'].explode().nunique()
    n_single = int((data['F2'].explode().value_counts() == 1).sum())
    print('Figure 2: ML methods')
    print(f'  Publications (reviews excluded): {len(data)}')
    print(f'  Distinct algorithms: {n_f2}; used in a single publication: {n_single}')
    save_figure(fig, output_dir, name)
