"""
Professional figure generation for PRISMA-ScR scoping review.
Publication-ready figures for Transboundary and Emerging Diseases (Wiley).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PASTELOWA PALETA PUBLIKACYJNA
# ============================================================================

def round_percentages_to_100(counts, decimals: int = 1) -> np.ndarray:
    """
    Round a list of counts to percentages that sum to exactly 100 using the
    largest-remainder method (each raw percentage is rounded down, then the
    values with the largest truncated remainder each get one extra unit
    until the total reaches 100.0) - required for pie/donut charts where
    naive independent rounding of each slice can leave the labels summing
    to e.g. 100.1%.
    """
    counts = np.asarray(counts, dtype=float)
    total = counts.sum()
    scale = 10 ** decimals
    raw = counts / total * 100 * scale

    floored = np.floor(raw)
    remainders = raw - floored
    shortfall = int(round(scale * 100 - floored.sum()))

    order = np.argsort(-remainders)
    floored[order[:shortfall]] += 1

    return floored / scale


PASTEL_PALETTE = {
    'HPAI': '#A8D8EA',
    'ASF': '#FFB3B3',
    'FMD': '#B4E7B3',
    'WNV': '#FFE5B4',
    'BTV': '#D4A5D4',
    'CSF': '#C9E4CA',
    'ND': '#FFD4D4',
    'LSD': '#FFC9B3',
    'General': '#E8D4F1',
    'Other': '#D3D3D3',
    'Zoonotic': '#F5D5A8',
}

ALGORITHM_PALETTE = {
    'Random Forest': '#A8D8EA',
    'XGBoost': '#FFB3B3',
    'Deep Learning': '#B4E7B3',
    'SVM': '#FFE5B4',
    'Spatial/GIS': '#D4A5D4',
    'Bayesian': '#C9E4CA',
    'NLP': '#FFD4D4',
    'Ensemble': '#FFC9B3',
    'Logistic Regression': '#E8D4F1',
    'Other': '#D3D3D3',
}

STAGE_PALETTE = {
    'Prediction/Forecasting': '#A8D8EA',
    'Surveillance': '#B4E7B3',
    'Spatial Modeling': '#D4A5D4',
    'Methodology/Review': '#FFE5B4',
    'Field': '#FFB3B3',
    'Diagnostics': '#FFD4D4',
    'Other': '#D3D3D3',
}

# ============================================================================
# FIGURE 1: TEMPORAL TREND (2016-2026) BY SECTION
# ============================================================================


def figure_1_temporal_trend(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Figure 1: Temporal distribution stacked by source (WoS, PubMed, Scopus)
    """
    
    # Nie filtruj Review - chcesz wszystkie publikacje za pierwsze źródła
    df = df.copy()
    
    print(f"\nFigure 1: Temporal Trend by Source")
    print(f"  Records analyzed: {len(df)}")
    
    # Mapowanie źródeł na kategorie
    source_map = {
        'WoS': '#A8D8EA',      # Niebieski
        'PubMed': '#B4E7B3',   # Zielony
        'Scopus': '#D4A5D4'    # Fioletowy
    }
    
    # Przygotuj dane
    years = sorted(df['Year'].unique())
    source_counts = {source: [] for source in source_map.keys()}
    
    for year in years:
        df_year = df[df['Year'] == year]
        year_data = {source: 0 for source in source_map.keys()}
        
        for _, row in df_year.iterrows():
            sources_str = str(row['Sources']).strip()
            sources_list = [s.strip() for s in sources_str.split(',')]
            
            # Rozbij na źródła
            for source in sources_list:
                if source in source_map:
                    year_data[source] += 1 / len(sources_list)
        
        for source in source_map.keys():
            source_counts[source].append(year_data[source])
    
    # Print summary
    for year, df_year in zip(years, [df[df['Year'] == y] for y in years]):
        print(f"  {year}: {len(df_year)} publications")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(7.09, 4.0), dpi=300)
    
    # Stacked bar chart
    bar_width = 0.6
    x_pos = np.arange(len(years))
    
    # Plot each source
    bottom = np.zeros(len(years))
    for source, color in source_map.items():
        values = source_counts[source]
        ax.bar(x_pos, values, bar_width, label=source, bottom=bottom,
               color=color, edgecolor='#FFFFFF', linewidth=1.0, alpha=0.9)
        bottom += np.array(values)
    
    # Trend line
    ax.plot(x_pos, bottom, color='#E74C3C', linewidth=2.5, linestyle='--', 
            label='Total Trend', marker='o', markersize=4, zorder=5)
    
    # Styling
    ax.set_xlabel('Year', fontsize=10, fontweight='bold', fontfamily='Arial')
    ax.set_ylabel('Number of Publications', fontsize=10, fontweight='bold', fontfamily='Arial')
    ax.set_title('Temporal Distribution of Publications by Source', fontsize=11, fontweight='bold',
                 fontfamily='Arial', pad=10)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(years, rotation=45)
    ax.set_xlim(-0.5, len(years) - 0.5)
    ax.set_ylim(0, bottom.max() * 1.15)
    
    # Grid
    ax.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    
    ax.tick_params(axis='both', labelsize=9, colors='#333333')
    
    # Legend
    ax.legend(loc='upper left', fontsize=9, framealpha=0.95, edgecolor='none')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.tight_layout()
    
    # Save
    png_path = output_dir / 'Figure_1_temporal_trend.png'
    svg_path = output_dir / 'Figure_1_temporal_trend.svg'
    
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(svg_path, bbox_inches='tight', facecolor='white')
    
    plt.close()
    
    print(f"  ✓ Saved: {png_path}")
    print(f"  ✓ Saved: {svg_path}")


# ============================================================================
# FIGURE 2: ALGORITHM vs DISEASE HEATMAP - Z FILTREM REVIEW
# ============================================================================

def figure_2_algorithm_disease_heatmap(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Figure 2: Heatmap of ML algorithms vs notifiable diseases.
    Expects the multi-label df from apply_algorithm_disease_standardization()
    - review exclusion already happened during that expansion.
    """

    df_clean = df.copy()

    # Top algorithms to show
    top_algos = ['Random Forest', 'Deep Learning', 'Spatial/GIS', 'XGBoost', 
                 'NLP', 'Bayesian', 'SVM', 'K-Means', 'Logistic Regression']
    
    # Core WOAH-8 diseases
    woah_8 = ['HPAI', 'ASF', 'FMD', 'WNV', 'BTV', 'CSF', 'ND', 'LSD']
    
    # Create crosstab
    heatmap_data = pd.crosstab(
        df_clean['Algorithm_standardized'],
        df_clean['Disease_standardized']
    )
    
    # Reorder rows and columns
    heatmap_data = heatmap_data.reindex(
        [a for a in top_algos if a in heatmap_data.index], 
        fill_value=0
    )
    heatmap_data = heatmap_data[[c for c in woah_8 if c in heatmap_data.columns]]
    
    print(f"\nFigure 2: Algorithm vs Disease Heatmap (multi-label)")
    print(f"  Algorithms shown: {list(heatmap_data.index)}")
    print(f"  Diseases shown: {list(heatmap_data.columns)}")
    print(f"  Records analyzed: {len(df_clean)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(7.09, 4.5), dpi=300)
    
    # Heatmap
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='d',
        cmap='RdYlGn_r',
        cbar_kws={'label': 'Number of Publications'},
        linewidths=0.5,
        linecolor='#E0E0E0',
        ax=ax,
        annot_kws={'fontsize': 9, 'fontweight': 'bold', 'fontfamily': 'Arial'},
        square=False,
        vmin=0,
        vmax=heatmap_data.max().max(),
    )
    
    # Styling
    ax.set_title('Machine Learning Algorithms vs. WOAH-Notifiable Diseases', 
                 fontsize=12, fontweight='bold', fontfamily='Arial', pad=15)
    ax.set_xlabel('Disease', fontsize=11, fontweight='bold', fontfamily='Arial')
    ax.set_ylabel('Algorithm', fontsize=11, fontweight='bold', fontfamily='Arial')
    
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10)
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=9)
    cbar.set_label('Number of Publications', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    png_path = output_dir / 'Figure_2_algorithm_disease_heatmap.png'
    svg_path = output_dir / 'Figure_2_algorithm_disease_heatmap.svg'
    
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(svg_path, bbox_inches='tight', facecolor='white')
    
    plt.close()
    
    print(f"  ✓ Saved: {png_path}")
    print(f"  ✓ Saved: {svg_path}")


# ============================================================================
# FIGURE 3: TOP 15 COUNTRIES (HORIZONTAL BAR CHART) 
# ============================================================================


def figure_3_top_countries_bar(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Figure 3: Top 15 countries - dyskretne kolorowe przedziały
    """
    
    # FILTER OUT REVIEW PAPERS
    df = df[df['Stage_standardized'] != 'Methodology/Review'].copy()
    df_geo = df[df['Country_standardized'].notna()].copy()
    
    # Count publications per country
    country_counts = df_geo['Country_standardized'].value_counts().head(15).sort_values()
    
    print(f"\nFigure 3: Top 15 Countries (excl. Review & metadata)")
    print(f"  Records analyzed: {len(df_geo)}")
    print(f"  Countries represented: {df_geo['Country_standardized'].nunique()}")
    print(f"  Top 15 countries:")
    for country, count in country_counts[::-1].items():
        pct = (count / len(df_geo)) * 100
        print(f"    {country:20s}: {count:2d} ({pct:4.1f}%)")
    
    # Categorical palette (one distinct hue per country/bar, not a
    # value-based ramp) - same OKLab construction as Figure 4's algorithm
    # colors (alternating lightness 0.70/0.82, chroma capped at 0.11 for a
    # soft, print-friendly look), with a rotated hue offset and reversed
    # lightness order so the two figures don't share colors. Assigned by
    # rank position (ascending, matching the sorted plot order) since
    # countries aren't a small fixed enumerable set like the algorithm
    # categories.
    COUNTRY_BAR_PALETTE = [
        '#FEA9B4', '#D88572', '#F9B27F', '#C2964B', '#D3C772',
        '#91AA5D', '#96D79B', '#4FB493', '#64DAD5', '#3AAFC7',
        '#81CFFD', '#75A0E1', '#BABEFD', '#AD8ED5', '#E9ACE9',
    ]
    colors = [COUNTRY_BAR_PALETTE[i % len(COUNTRY_BAR_PALETTE)] for i in range(len(country_counts))]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(7.09, 4.5), dpi=300)
    
    # Horizontal bar chart
    bars = ax.barh(range(len(country_counts)), country_counts.values,
                   color=colors, edgecolor='#555555', linewidth=1.0, alpha=0.9)
    
    # Add value labels
    for i, (country, count) in enumerate(country_counts.items()):
        ax.text(count + 0.5, i, str(int(count)), va='center', fontsize=9, 
                fontweight='bold', fontfamily='Arial', color='#333333')
    
    # Styling
    ax.set_yticks(range(len(country_counts)))
    ax.set_yticklabels(country_counts.index, fontsize=10, fontfamily='Arial')
    ax.set_xlabel('Number of Publications', fontsize=11, fontweight='bold', fontfamily='Arial')
    ax.set_title('Top 15 Countries by Publication Count', fontsize=12, fontweight='bold',
                 fontfamily='Arial', pad=15)
    
    ax.set_xlim(0, country_counts.max() * 1.15)
    ax.grid(axis='x', alpha=0.2, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.tick_params(axis='x', labelsize=9, colors='#333333')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    plt.tight_layout()
    
    # Save
    png_path = output_dir / 'Figure_3_top_countries_bar.png'
    svg_path = output_dir / 'Figure_3_top_countries_bar.svg'
    
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(svg_path, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  ✓ Saved: {png_path}")
    print(f"  ✓ Saved: {svg_path}")

# ============================================================================
# FIGURE 3B: WORLD MAP - ALL COUNTRIES WITH DATA
# ============================================================================

def figure_3b_countries_map(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Figure 3b: World map showing all countries with publication data.
    Excludes Methodology/Review papers and metadata entries.
    Shows every country that contributed at least 1 study.
    """
    
    import geopandas as gpd
    from matplotlib.colors import LinearSegmentedColormap

    # Single-hue pastel teal ramp (light -> dark), same teal family as the
    # Figure 3 country-bar palette ('#3AAFC7'/'#4FB493') so the two country
    # figures read as one system instead of the old high-saturation
    # yellow-orange-red heat ramp, which also broke the "sequential = one
    # hue" rule and didn't match anything else in the report.
    PASTEL_TEAL_SEQUENTIAL = LinearSegmentedColormap.from_list(
        'pastel_teal', ['#E3F5F1', '#A9E0D3', '#5CC4AC', '#2B8F79', '#145F4F']
    )

    try:
        # FILTER OUT REVIEW PAPERS
        df = df[df['Stage_standardized'] != 'Methodology/Review'].copy()
        
        # FILTER OUT metadata entries (None values)
        df_geo = df[df['Country_standardized'].notna()].copy()
        
        # Count publications per country
        country_counts = df_geo['Country_standardized'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Count']
        
        print(f"\nFigure 3b: World Map - All Countries (excl. Review & metadata)")
        print(f"  Records analyzed: {len(df_geo)}")
        print(f"  Countries with data: {len(country_counts)}")
        print(f"  Top 10 countries:")
        for _, row in country_counts.head(10).iterrows():
            pct = (row['Count'] / len(df_geo)) * 100
            print(f"    {row['Country']:20s}: {row['Count']:2d} ({pct:4.1f}%)")
        
        # Load world map
        print(f"  Loading world map...")
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        world = gpd.read_file(url)
        
        # Manual mapping of our countries to world map names
        country_mapping_for_map = {
            'USA': 'United States of America',
            'China': 'China',
            'UK': 'United Kingdom',
            'South Korea': 'South Korea',
            'Canada': 'Canada',
            'Italy': 'Italy',
            'France': 'France',
            'Spain': 'Spain',
            'Australia': 'Australia',
            'Japan': 'Japan',
            'Thailand': 'Thailand',
            'Germany': 'Germany',
            'Poland': 'Poland',
            'Romania': 'Romania',
            'New Zealand': 'New Zealand',
            'India': 'India',
            'Russia': 'Russia',
            'Uganda': 'Uganda',
            'Egypt': 'Egypt',
            'Ethiopia': 'Ethiopia',
            'Pakistan': 'Pakistan',
            'Bangladesh': 'Bangladesh',
            'Malaysia': 'Malaysia',
            'Indonesia': 'Indonesia',
            'Iran': 'Iran',
            'Ireland': 'Ireland',
            'Netherlands': 'Netherlands',
            'Switzerland': 'Switzerland',
            'Taiwan': 'Taiwan',
            'Kuwait': 'Kuwait',
            'Zambia': 'Zambia',
            'Madagascar': 'Madagascar',
        }
        
        # Map our countries to world map names
        country_counts['world_name'] = country_counts['Country'].map(country_mapping_for_map)
        
        # Merge with world
        world_merged = world.merge(country_counts, left_on='NAME', right_on='world_name', how='left')
        world_merged['Count'] = world_merged['Count'].fillna(0)
        
        print(f"  Creating map...")
        fig, ax = plt.subplots(figsize=(7.09, 4.0), dpi=300)
        
        # Base map - soft warm-neutral grey for "no data", well clear of the
        # teal data ramp so it reads as absence rather than a low value
        world_merged.plot(ax=ax, color='#EDEDE9', edgecolor='#D6D6D0', linewidth=0.5)

        # Countries with data
        world_data = world_merged[world_merged['Count'] > 0]
        world_data.plot(
            ax=ax,
            column='Count',
            cmap=PASTEL_TEAL_SEQUENTIAL,
            edgecolor='#5B6B64',
            linewidth=0.7,
            legend=True,
            legend_kwds={
                'label': 'Number of Publications',
                'orientation': 'vertical',
                'shrink': 0.7
            },

        )

        # Styling
        ax.set_title('Geographic Distribution: All Countries with Publications',
                     fontsize=12, fontweight='bold', fontfamily='Arial', pad=15)
        ax.set_xlim([-180, 180])
        ax.set_ylim([-60, 85])
        ax.axis('off')

        cbar = fig.axes[-1]
        cbar.set_ylabel('Number of Publications', fontsize=10, fontweight='bold', fontfamily='Arial')
        cbar.tick_params(labelsize=9)

        fig.patch.set_facecolor('white')

        plt.tight_layout()
        
        # Save
        png_path = output_dir / 'Figure_3b_countries_map.png'
        svg_path = output_dir / 'Figure_3b_countries_map.svg'
        
        fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
        fig.savefig(svg_path, bbox_inches='tight', facecolor='white')
        
        plt.close()
        
        print(f"  ✓ Saved: {png_path}")
        print(f"  ✓ Saved: {svg_path}")
        
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

# ============================================================================
# FIGURE 4: TOP 15 ALGORITHMS (HORIZONTAL BAR CHART)
# ============================================================================

def figure_4_top_algorithms_bar(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Figure 4: Top 15 machine learning algorithms by frequency (multi-label -
    a publication counts toward every algorithm category it mentions).
    Expects the df from apply_algorithm_standardization() - review exclusion
    already happened during that expansion.
    """

    df_algo = df.copy()

    # Count algorithms
    algo_counts = df_algo['Algorithm_standardized'].value_counts().head(15).sort_values()

    print(f"\nFigure 4: Top 15 Algorithms (multi-label)")
    print(f"  Records analyzed: {len(df_algo)}")
    print(f"  Algorithms shown: {len(algo_counts)}")
    for algo, count in algo_counts[::-1].items():
        pct = (count / len(df_algo)) * 100
        print(f"    {algo:25s}: {count:2d} ({pct:5.1f}%)")
    
    # Color mapping - covers every category in ALGORITHM_STANDARDIZATION_KEY
    # (see src/standardization_mappings.py) so no category falls back to gray.
    # Colors were generated in OKLab with alternating lightness (0.70/0.82)
    # and a moderate chroma cap (0.11) to keep a soft, print-friendly pastel
    # look while still maximizing pairwise separation across all 16
    # categories (min pairwise dE ~7.2, vs ~2-3 for evenly-spaced pastel
    # tints at one lightness). This falls a bit short of the strict dE>=8
    # CVD-safe target - unavoidable at 16 simultaneous categories without
    # going more saturated - but bars are already directly labeled with the
    # algorithm name, so color here is a secondary, not sole, identity
    # channel.
    algo_colors = {
        'K-Means': '#D5829C',
        'Network Analysis': '#FEABA7',
        'Feature Selection': '#D68865',
        'Time Series': '#F2B777',
        'Statistical Regression': '#B89B4A',
        'KNN': '#C5CC78',
        'NLP': '#81AD69',
        'Bayesian': '#86D9A9',
        'Decision Tree': '#41B4A1',
        'Ensemble': '#62D9E2',
        'Logistic Regression': '#46ACD0',
        'SVM': '#93CAFD',
        'Spatial/GIS': '#859BE1',
        'XGBoost': '#C5B9FD',
        'Deep Learning': '#B78ACC',
        'Random Forest': '#F1A9DD',
    }
    colors = [algo_colors.get(algo, '#D3D3D3') for algo in algo_counts.index]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(7.09, 5.0), dpi=300)
    
    # Horizontal bar chart
    bars = ax.barh(range(len(algo_counts)), algo_counts.values,
                   color=colors, edgecolor='#555555', linewidth=1.0, alpha=0.85)
    
    # Add value labels on bars
    for i, (algo, count) in enumerate(algo_counts.items()):
        ax.text(count + 0.5, i, str(int(count)), va='center', fontsize=9, 
                fontweight='bold', fontfamily='Arial')
    
    # Styling
    ax.set_yticks(range(len(algo_counts)))
    ax.set_yticklabels(algo_counts.index, fontsize=10, fontfamily='Arial')
    ax.set_xlabel('Number of Publications', fontsize=11, fontweight='bold', fontfamily='Arial')
    ax.set_title('Top 15 Machine Learning Algorithms', fontsize=12, fontweight='bold',
                 fontfamily='Arial', pad=15)
    
    ax.set_xlim(0, algo_counts.max() * 1.15)
    
    # Grid
    ax.grid(axis='x', alpha=0.2, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    
    ax.tick_params(axis='x', labelsize=9, colors='#333333')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.tight_layout()
    
    # Save
    png_path = output_dir / 'Figure_4_top_algorithms_bar.png'
    svg_path = output_dir / 'Figure_4_top_algorithms_bar.svg'
    
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(svg_path, bbox_inches='tight', facecolor='white')
    
    plt.close()
    
    print(f"  ✓ Saved: {png_path}")
    print(f"  ✓ Saved: {svg_path}")


# ============================================================================
# FIGURE 5: STAGE DISTRIBUTION (PIE/DONUT CHART)
# ============================================================================

def figure_5_stage_distribution(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Figure 5: Pie chart z liniami pomocniczymi - ulepszone rozmieszczenie
    """
    
    from matplotlib.patches import Circle
    import matplotlib.patches as mpatches
    
    df = df.copy()

    # Count by stage (Methodology/Review included as its own category)
    stage_counts = df['Stage_standardized'].value_counts()

    stage_pcts = round_percentages_to_100(stage_counts.values)

    print(f"\nFigure 5: Stage Distribution (incl. Methodology/Review)")
    print(f"  Records analyzed: {len(df)}")
    print(f"  Stages shown: {len(stage_counts)}")
    for stage, count, pct in zip(stage_counts.index, stage_counts.values, stage_pcts):
        print(f"    {stage:25s}: {count:3d} ({pct:5.1f}%)")

    # Color mapping
    stage_colors = {
        'Prediction/Forecasting': '#A8D8EA',
        'Surveillance': '#B4E7B3',
        'Spatial Modeling': '#D4A5D4',
        'Field': '#FFB3B3',
        'Diagnostics': '#FFE5B4',
        'Methodology/Review': "#E4C9CF",
        'Other': '#D3D3D3',
    }
    colors = [stage_colors.get(stage, '#D3D3D3') for stage in stage_counts.index]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(9.0, 6.5), dpi=300)
    
    # Pie chart bez autopct
    wedges, texts = ax.pie(
        stage_counts.values,
        colors=colors,
        startangle=45,  # Zmieniony kąt
        wedgeprops={'edgecolor': '#FFFFFF', 'linewidth': 2.5}
    )
    
    # Draw donut hole
    centre_circle = Circle((0, 0), 0.70, fc='white', edgecolor='#FFFFFF', linewidth=2)
    ax.add_artist(centre_circle)
    
    # Dodaj procenty z leader lines - ulepszone rozmieszczenie
    radius_line = 1.05
    radius_text = 1.5
    
    for i, (wedge, stage, count, pct) in enumerate(zip(wedges, stage_counts.index, stage_counts.values, stage_pcts)):
        # Oblicz kąt środkowy segmentu
        ang = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
        angle = ang * np.pi / 180.0
        
        # Pozycja linii
        x_line = radius_line * np.cos(angle)
        y_line = radius_line * np.sin(angle)
        
        # Pozycja tekstu
        if np.cos(angle) > 0:
            x_text = radius_text * np.cos(angle) + 0.2
            ha = 'left'
        else:
            x_text = radius_text * np.cos(angle) - 0.2
            ha = 'right'
        
        y_text = radius_text * np.sin(angle)
        
        # Specjalne przesunięcie dla Diagnostics (żółty)
        if stage == 'Diagnostics':
            y_text += 0.35
        
        # Kolor linii = kolor segmentu
        line_color = colors[i]
        
        # Draw leader line
        ax.plot([x_line, x_text], [y_line, y_text], color=line_color, linewidth=2.0, zorder=3)
        
        # Procent
        pct_text = f"{pct:.1f}%"
        
        # Draw text box (black text for readability on white - the colored
        # edge still ties the label back to its segment)
        ax.text(x_text, y_text, pct_text,
                ha=ha, va='center',
                fontsize=10, fontweight='bold', fontfamily='Arial',
                color='#1A1A1A',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                         edgecolor=line_color, linewidth=1.5, alpha=0.97),
                zorder=4)
    
    # Title
    ax.set_title('Distribution of Publications by Application Stage', 
                 fontsize=12, fontweight='bold', fontfamily='Arial', pad=20)
    
    # Legend na boku
    legend_elements = [mpatches.Patch(facecolor=stage_colors.get(stage, '#D3D3D3'), 
                                      edgecolor='#555555', linewidth=1,
                                      label=f"{stage}")
                      for stage in stage_counts.index]
    
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.0, 0, 0.5, 1),
              fontsize=10, frameon=True, fancybox=False, edgecolor='#CCCCCC')
    
    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(-2.0, 2.0)
    ax.set_aspect('equal')
    
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    
    # Save
    png_path = output_dir / 'Figure_5_stage_distribution.png'
    svg_path = output_dir / 'Figure_5_stage_distribution.svg'
    
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(svg_path, bbox_inches='tight', facecolor='white')
    
    plt.close()
    
    print(f"  ✓ Saved: {png_path}")
    print(f"  ✓ Saved: {svg_path}")
# ============================================================================
# GENERATE ALL FIGURES
# ============================================================================

def generate_all_figures(df_pub: pd.DataFrame, df_algo_disease: pd.DataFrame,
                          df_algo: pd.DataFrame, df_country: pd.DataFrame,
                          output_dir: Path) -> None:
    """
    Generate Figures 1-5 (and 3b) into output_dir.

    df_pub: publication-level standardized data (one row per publication -
        apply_publication_level_standardization output, same construction as
        Table S2) - used for Figures 1 and 5, where each publication must
        count exactly once. Do NOT pass apply_standardization()'s expanded
        output here: it duplicates rows by disease x country combinations,
        which silently inflates Year/Stage counts for any publication
        studying multiple diseases/countries.
    df_algo_disease: multi-label algorithm x disease expansion
        (apply_algorithm_disease_standardization output) - used for Figure 2.
    df_algo: multi-label algorithm-only expansion (apply_algorithm_standardization
        output) - used for Figure 4.
    df_country: multi-label country-only expansion (apply_country_standardization
        output) - used for Figures 3 and 3b.
    """
    figure_1_temporal_trend(df_pub, output_dir)
    figure_2_algorithm_disease_heatmap(df_algo_disease, output_dir)
    figure_3_top_countries_bar(df_country, output_dir)
    figure_3b_countries_map(df_country, output_dir)
    figure_4_top_algorithms_bar(df_algo, output_dir)
    figure_5_stage_distribution(df_pub, output_dir)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    from src.data_cleaning import load_data, remove_excluded
    from src.standardization import (
        apply_publication_level_standardization,
        apply_algorithm_standardization,
        apply_algorithm_disease_standardization,
        apply_country_standardization,
    )

    # Load data
    data_path = Path("data/data_ml_publications.xlsx")
    df = load_data(data_path)
    df_clean = remove_excluded(df)

    # Standardize
    df_pub_standard = apply_publication_level_standardization(df_clean)
    df_algo_disease_standard = apply_algorithm_disease_standardization(df_clean)
    df_algo_standard = apply_algorithm_standardization(df_clean)
    df_country_standard = apply_country_standardization(df_clean)

    # Create output directory
    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)

    generate_all_figures(df_pub_standard, df_algo_disease_standard, df_algo_standard,
                          df_country_standard, output_dir)

    print("\n" + "="*80)
    print("Figure generation complete!")
    print("="*80)