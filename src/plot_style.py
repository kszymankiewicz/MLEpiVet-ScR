"""
Shared styling and ordering helpers for all figures.
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from src.mappings import (
    CATEGORY_COLORS, CATEGORY_FAMILIES, CATEGORY_FAMILY, DISEASE_HOST_GROUPS, OTHER_CATEGORY,
)

TEXT_COLOR = '#333333'
EDGE_COLOR = '#555555'
GRID_COLOR = '#E0E0E0'

# One colour per host group, used for diseases in every figure.
HOST_COLORS = {
    'Poultry': '#F5D5A8',
    'Ruminants': '#B4E7B3',
    'Swine': '#FFB3B3',
    'Multi-host / zoonotic': '#A8D8EA',
    'Equids': '#D4A5D4',
}


def apply_style() -> None:
    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': 8,
        'axes.edgecolor': TEXT_COLOR,
        'axes.labelcolor': TEXT_COLOR,
        'xtick.color': TEXT_COLOR,
        'ytick.color': TEXT_COLOR,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'svg.fonttype': 'none',
    })


def save_figure(fig: plt.Figure, output_dir: Path, name: str) -> None:
    """Save as 300-dpi PNG and editable SVG."""
    for ext in ('png', 'svg'):
        path = output_dir / f'{name}.{ext}'
        fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f'  Saved: {path}')
    plt.close(fig)


def category_color(category: str) -> str:
    return CATEGORY_COLORS.get(category, CATEGORY_COLORS[OTHER_CATEGORY])


def panel_label(ax, letter: str, x: float = -0.02, y: float = 1.02) -> None:
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=12,
            fontweight='bold', ha='right', va='bottom')


def family_category_order(df: pd.DataFrame) -> list:
    """
    [(family, n_family_pubs, [(category, n_pubs), ...]), ...]

    Families sorted by number of publications using any of their
    categories; categories within a family sorted by publication count.
    Counts are publications (a publication counts once per family/category).
    """
    cat_counts = df['F1'].explode().value_counts()
    fam_counts = df['F1'].map(lambda cats: {CATEGORY_FAMILY[c] for c in cats}).explode().value_counts()
    order = []
    for family in fam_counts.index:
        cats = [(c, int(cat_counts.get(c, 0))) for c in CATEGORY_FAMILIES[family]
                if cat_counts.get(c, 0) > 0]
        cats.sort(key=lambda x: -x[1])
        order.append((family, int(fam_counts[family]), cats))
    return order


def disease_groups(counts: pd.Series) -> list:
    """
    [(host group, [diseases sorted by publications])] for diseases present
    in counts; groups sorted by total publications. Shared by Figures 3-5.
    """
    groups = []
    for host, diseases in DISEASE_HOST_GROUPS.items():
        present = sorted((d for d in diseases if counts.get(d, 0) > 0), key=lambda d: -counts[d])
        if present:
            groups.append((host, present))
    groups.sort(key=lambda g: -sum(counts[d] for d in g[1]))
    return groups


def fit_text(ax, x: float, y: float, width: float, height: float, text: str,
             max_size: float = 6.5, min_size: float = 4.5, **kwargs):
    """
    Draw text centred at (x, y) so that it fits a width x height box in data
    units: try the text on one line, then broken at ' / ', then one word per
    line, shrinking the font in 0.25-pt steps until it fits (never below
    min_size). Returns the Text artist.
    """
    words = text.replace(' / ', '/ ').split(' ')
    candidates = [text, text.replace(' / ', '/\n'), '\n'.join(words)]
    renderer = ax.figure.canvas.get_renderer()
    to_data = ax.transData.inverted()
    kwargs = {'ha': 'center', 'va': 'center', 'linespacing': 1.0, **kwargs}
    size = max_size
    while True:
        for candidate in candidates:
            artist = ax.text(x, y, candidate, fontsize=size, **kwargs)
            (x0, y0), (x1, y1) = to_data.transform(artist.get_window_extent(renderer))
            if abs(x1 - x0) <= width and abs(y1 - y0) <= height:
                return artist
            artist.remove()
        if size <= min_size:
            return ax.text(x, y, candidates[-1], fontsize=min_size, **kwargs)
        size = max(min_size, size - 0.25)
