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
