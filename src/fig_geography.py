"""
Figure 3: geography and disease coverage (review articles excluded).

  A - map. Fill: publications whose geographical scope includes the
      country (named countries, plus every country of a continent for
      continental studies; global studies are reported in a note, not
      mapped). Circles: publications with country-specific data.
  B - publications per WOAH-listed viral disease, grouped by host.

Figure S1: publications per explicitly named country (bar chart).
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Patch

from src.mappings import COUNTRY_TO_NATURAL_EARTH, REGION_CONTINENTS
from src.plot_style import (
    EDGE_COLOR, HOST_COLORS, TEXT_COLOR, apply_style, disease_groups, fit_text, panel_label,
    save_figure,
)

NATURAL_EARTH_URL = ('https://naciscdn.org/naturalearth/50m/cultural/'
                     'ne_50m_admin_0_countries.zip')
EXCLUDED_CONTINENTS = {'Antarctica', 'Seven seas (open ocean)'}
MAP_CRS = 'ESRI:54030'  # Robinson
MIN_PUBLICATIONS_BAR = 2

CONTINENT_COLORS = {
    'Asia': '#FFB3B3',
    'Europe': '#A8D8EA',
    'North America': '#B4E7B3',
    'Africa': '#FFE5B4',
    'South America': '#C9E4CA',
    'Oceania': '#D4A5D4',
}

def load_world() -> gpd.GeoDataFrame:
    world = gpd.read_file(NATURAL_EARTH_URL)
    return world[~world['CONTINENT'].isin(EXCLUDED_CONTINENTS)].reset_index(drop=True)


def _ne_name(country: str) -> str:
    return COUNTRY_TO_NATURAL_EARTH.get(country, country)


def coverage_counts(df: pd.DataFrame, world: gpd.GeoDataFrame) -> pd.Series:
    """Publications per Natural Earth country, continents expanded, 'Global' skipped."""
    continent_of = dict(zip(world['ADMIN'], world['CONTINENT']))
    unknown = sorted({_ne_name(c) for c in df['country_list'].explode().dropna()} - set(continent_of))
    if unknown:
        raise ValueError(f'Countries not found in Natural Earth: {unknown}')

    counts = pd.Series(0, index=world['ADMIN'])
    for countries, regions in zip(df['country_list'], df['region_list']):
        scope = {_ne_name(c) for c in countries}
        for region in regions:
            continent = REGION_CONTINENTS[region]
            if continent is None:  # 'Global' - reported in a note instead
                continue
            scope |= {a for a, cont in continent_of.items() if continent in (None, cont)}
        counts[list(scope)] += 1
    return counts


def figure_s1_countries_bar(df: pd.DataFrame, world: gpd.GeoDataFrame, output_dir: Path) -> None:
    continent_of = dict(zip(world['ADMIN'], world['CONTINENT']))
    counts = df['country_list'].explode().dropna().value_counts()
    min_n = MIN_PUBLICATIONS_BAR if (counts >= MIN_PUBLICATIONS_BAR).any() else 1
    shown = counts[counts >= min_n]
    singles = sorted(counts[counts < min_n].index)

    fig, ax = plt.subplots(figsize=(4.5, 5.6))
    y = np.arange(len(shown))
    colors = [CONTINENT_COLORS[continent_of[_ne_name(c)]] for c in shown.index]
    ax.barh(y, shown.values, color=colors, edgecolor=EDGE_COLOR, linewidth=0.6, height=0.72)
    for yi, n in zip(y, shown.values):
        ax.text(n + 0.25, yi, str(n), va='center', fontsize=7, color=TEXT_COLOR)
    ax.set_yticks(y)
    ax.set_yticklabels(shown.index, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlim(0, shown.max() * 1.12)
    ax.set_xlabel('Number of publications', fontweight='bold')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis='x', color='#EEEEEE', lw=0.5)
    ax.set_axisbelow(True)

    present = [c for c in CONTINENT_COLORS
               if c in {continent_of[_ne_name(x)] for x in shown.index}]
    ax.legend(handles=[Patch(facecolor=CONTINENT_COLORS[c], edgecolor=EDGE_COLOR,
                             linewidth=0.5, label=c) for c in present],
              loc='lower right', fontsize=7, frameon=False, title='Continent',
              title_fontsize=7.5)

    print('Figure S1: publications per country')
    print(f'  Countries named: {len(counts)}; shown (>= {min_n}): {len(shown)}')
    print(f'  Countries with one publication ({len(singles)}): {", ".join(singles)}')
    save_figure(fig, output_dir, 'Figure_S1_countries_bar')


# Coverage classes (lower bounds): none, 1-2, 3-5, 6-9, 10+ publications.
COVERAGE_CLASS_BOUNDS = [0, 1, 3, 6, 10]
COVERAGE_CLASS_COLORS = ['#ECECE8', '#C9EAE2', '#7FD0BC', '#2E9C83', '#145F4F']
OCEAN_COLOR = '#F3F7FA'
GRATICULE_COLOR = '#DCE5EC'
BUBBLE_FACE = '#F08A80'
BUBBLE_EDGE = '#9E3B33'
BUBBLE_SCALE = 16          # marker area (pt^2) per publication
EUROPE_BOX = (-12, 35, 40, 71)   # lon_min, lat_min, lon_max, lat_max
MAP_LAT_MIN = -58


def _project_line(lons, lats) -> gpd.GeoSeries:
    from shapely.geometry import LineString
    return gpd.GeoSeries([LineString(zip(lons, lats))], crs='EPSG:4326').to_crs(MAP_CRS)


def _sphere(lat_min: float = -90) -> gpd.GeoSeries:
    from shapely.geometry import Polygon
    lons = np.linspace(-180, 180, 361)
    lats = np.linspace(lat_min, 90, 181)
    ring = ([(-180, la) for la in lats] + [(lo, 90) for lo in lons]
            + [(180, la) for la in lats[::-1]] + [(lo, lat_min) for lo in lons[::-1]])
    return gpd.GeoSeries([Polygon(ring)], crs='EPSG:4326').to_crs(MAP_CRS)


def _box(lon_min, lat_min, lon_max, lat_max) -> gpd.GeoSeries:
    from shapely.geometry import Polygon
    n = 50
    ring = ([(lo, lat_min) for lo in np.linspace(lon_min, lon_max, n)]
            + [(lon_max, la) for la in np.linspace(lat_min, lat_max, n)]
            + [(lo, lat_max) for lo in np.linspace(lon_max, lon_min, n)]
            + [(lon_min, la) for la in np.linspace(lat_max, lat_min, n)])
    return gpd.GeoSeries([Polygon(ring)], crs='EPSG:4326').to_crs(MAP_CRS)


def _anchor_points(world: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """Representative point of each country's largest polygon (mainland)."""
    parts = world[['ADMIN', 'geometry']].explode(index_parts=False)
    parts = parts.assign(area=parts.geometry.area).sort_values('area', ascending=False)
    largest = parts.drop_duplicates('ADMIN').set_index('ADMIN')
    return largest.geometry.representative_point()


def _coverage_class(value: float) -> int:
    return max(i for i, lo in enumerate(COVERAGE_CLASS_BOUNDS) if value >= lo)


def _class_labels(vmax: int) -> list:
    labels = ['None']
    bounds = COVERAGE_CLASS_BOUNDS[1:] + [None]
    for lo, nxt in zip(bounds[:-1], bounds[1:]):
        hi = nxt - 1 if nxt is not None else vmax
        labels.append(f'{lo}–{hi}' if hi > lo else f'{lo}')
    return labels


def _draw_layers(ax, world, bubbles, show_bubble, label_min=3) -> None:
    world.plot(ax=ax, color=world['fill'], edgecolor='white', linewidth=0.25, zorder=2)
    for name, (pt, n) in bubbles.items():
        if not show_bubble(pt):
            continue
        ax.scatter(pt.x, pt.y, s=n * BUBBLE_SCALE, color=BUBBLE_FACE, alpha=0.88,
                   edgecolor=BUBBLE_EDGE, linewidth=0.6, zorder=4)
        if n >= label_min:
            ax.text(pt.x, pt.y, str(n), ha='center', va='center', fontsize=5.5,
                    fontweight='bold', color='white', zorder=5)


def _draw_map(ax, df: pd.DataFrame, world: gpd.GeoDataFrame) -> None:
    counts = coverage_counts(df, world)
    vmax = int(counts.max())
    world = world.assign(coverage=world['ADMIN'].map(counts))
    world['fill'] = [COVERAGE_CLASS_COLORS[_coverage_class(v)] for v in world['coverage']]
    world = world.to_crs(MAP_CRS)

    named = df['country_list'].explode().dropna().map(_ne_name).value_counts()
    anchors = _anchor_points(world)
    bubbles = {c: (anchors[c], int(n)) for c, n in named.items()}

    # Inset frame: projected bounding rectangle of the Europe lon/lat box.
    ex0, ey0, ex1, ey1 = _box(*EUROPE_BOX).total_bounds
    mx, my = (ex1 - ex0) * 0.04, (ey1 - ey0) * 0.04
    in_europe = lambda pt: ex0 + mx <= pt.x <= ex1 - mx and ey0 + my <= pt.y <= ey1 - my

    sphere = _sphere(MAP_LAT_MIN)
    sphere.plot(ax=ax, color=OCEAN_COLOR, edgecolor='#B8C4CE', linewidth=0.6, zorder=0)
    for lon in range(-180, 181, 30):
        _project_line([lon] * 50, np.linspace(MAP_LAT_MIN, 90, 50)).plot(
            ax=ax, color=GRATICULE_COLOR, linewidth=0.3, zorder=1)
    for lat in range(-30, 90, 30):
        _project_line(np.linspace(-180, 180, 100), [lat] * 100).plot(
            ax=ax, color=GRATICULE_COLOR, linewidth=0.3, zorder=1)
    _draw_layers(ax, world, bubbles, show_bubble=lambda pt: not in_europe(pt))
    ax.add_patch(plt.Rectangle((ex0, ey0), ex1 - ex0, ey1 - ey0, fill=False,
                               edgecolor='#555555', linewidth=0.7, linestyle='--', zorder=6))
    ax.set_axis_off()
    x0, y0, x1, y1 = sphere.total_bounds
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)

    ins = ax.inset_axes([0.0, 0.0, 0.30, 0.47])
    ins.set_facecolor(OCEAN_COLOR)
    _draw_layers(ins, world, bubbles, show_bubble=in_europe, label_min=2)
    ins.set_xlim(ex0, ex1)
    ins.set_ylim(ey0, ey1)
    ins.set_xticks([])
    ins.set_yticks([])
    for spine in ins.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor('#555555')
        spine.set_linewidth(0.7)
        spine.set_linestyle('--')
    ins.text(0.03, 0.97, 'Europe', transform=ins.transAxes, ha='left', va='top',
             fontsize=6.5, fontweight='bold', color=TEXT_COLOR)

    n_global = int(df['region_list'].map(lambda r: 'Global' in r).sum())
    class_handles = [Patch(facecolor=c, edgecolor='#BBBBBB', linewidth=0.4, label=l)
                     for c, l in zip(COVERAGE_CLASS_COLORS, _class_labels(vmax))]
    leg = ax.legend(handles=class_handles, loc='upper left', bbox_to_anchor=(0.0, -0.01),
                    ncol=5, fontsize=6.5, frameon=False, handlelength=1.6, columnspacing=0.9,
                    title='Publications with data from the country\n(named or continent-wide)',
                    title_fontsize=6.8)
    leg._legend_box.align = 'left'
    ax.add_artist(leg)
    sizes = [2, 5, 10, int(named.max())]
    bubble_handles = [plt.scatter([], [], s=n * BUBBLE_SCALE, color=BUBBLE_FACE, alpha=0.88,
                                  edgecolor=BUBBLE_EDGE, linewidth=0.6, label=str(n))
                      for n in sizes]
    ax.legend(handles=bubble_handles, loc='upper right', bbox_to_anchor=(1.0, -0.01),
              ncol=len(sizes), fontsize=6.5, frameon=False, columnspacing=1.2,
              handletextpad=0.6, title='Country-specific studies', title_fontsize=6.8,
              scatterpoints=1, borderpad=0.8)
    ax.text(0.5, -0.03, f'Global-scope studies (n = {n_global}) are not mapped.',
            transform=ax.transAxes, ha='center', va='top', fontsize=6.5, style='italic',
            color='#555555')

    print(f'  Map: global-scope studies not mapped: {n_global}')
    print('  Highest coverage: ' + ', '.join(
        f'{c} {n}' for c, n in counts.sort_values(ascending=False).head(8).items()))
    print(f'  Countries with no coverage: {(counts == 0).sum()} of {len(counts)}')


def _draw_disease_bars(ax, df: pd.DataFrame) -> None:
    counts = df['disease_list'].explode().value_counts()
    x, ticks, labels, group_labels = 0.0, [], [], []
    for host, diseases in disease_groups(counts):
        start = x
        for d in diseases:
            ax.bar(x, counts[d], width=0.75, color=HOST_COLORS[host],
                   edgecolor=EDGE_COLOR, linewidth=0.5)
            ax.text(x, counts[d] + 0.6, str(counts[d]), ha='center', va='bottom',
                    fontsize=6.5, color=TEXT_COLOR)
            ticks.append(x)
            labels.append(d)
            x += 1
        group_labels.append(((start + x - 1) / 2, x - start + 0.2, host))
        ax.plot([start - 0.35, x - 0.65], [-6.6, -6.6], color='#888888', lw=0.8, clip_on=False)
        x += 0.6
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=7, fontweight='bold')
    ax.tick_params(axis='x', length=0)
    ax.set_xlim(-0.6, x - 0.9)
    ax.set_ylim(0, counts.max() * 1.15)
    ax.set_ylabel('Number of publications', fontweight='bold')
    ax.grid(axis='y', color='#EEEEEE', lw=0.5)
    ax.set_axisbelow(True)
    # Drawn after the axis limits are fixed so fit_text measures correctly.
    for cx, width, host in group_labels:
        fit_text(ax, cx, -11.0, width, 7.0, host, max_size=6.8, fontweight='bold',
                 clip_on=False)


def figure_3_geography_diseases(df: pd.DataFrame, world: gpd.GeoDataFrame, output_dir: Path) -> None:
    fig = plt.figure(figsize=(7.2, 6.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 0.42], hspace=0.30)
    ax_map = fig.add_subplot(gs[0])
    ax_bar = fig.add_subplot(gs[1])
    print('Figure 3: geography and diseases')
    _draw_map(ax_map, df, world)
    _draw_disease_bars(ax_bar, df)
    panel_label(ax_map, 'A', x=0.0, y=0.98)
    panel_label(ax_bar, 'B', x=-0.06, y=1.02)
    save_figure(fig, output_dir, 'Figure_3_geography')


def figure_3_geography(df: pd.DataFrame, output_dir: Path) -> None:
    apply_style()
    data = df[~df['is_review']]
    world = load_world()
    figure_3_geography_diseases(data, world, output_dir)
    figure_s1_countries_bar(data, world, output_dir)
