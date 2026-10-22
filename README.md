# MLEpiVet-ScR

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23040937.svg)](https://doi.org/10.5281/zenodo.23040937)

**Data processing and visualization pipeline for a scoping review of machine learning in notifiable animal disease epidemiology**

Analysis code for the PRISMA-ScR scoping review: "Application of Machine Learning Methods in the Epidemiology of Notifiable Animal Diseases"

## Overview

This repository contains the Python pipeline used to standardise the
extracted data and produce the figures and supplementary table of the review.
It covers machine-learning studies on WOAH-listed viral diseases of animals.

**Included publications:** 109 (100 primary studies, 9 reviews)
**Sources:** PubMed, Scopus, Web of Science (May-June 2026)
**Target journal:** Transboundary and Emerging Diseases (Wiley)

## Installation

```bash
# Clone repository
git clone https://github.com/kszymankiewicz/MLEpiVet-ScR.git
cd MLEpiVet-ScR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

Copy `template/data_template.xlsx` to `data/data_final.xlsx` and replace the
example rows with your own extracted records (column schema and coding rules
in [template/README.md](template/README.md)), then run:

```bash
python main.py
# or with explicit paths
python main.py --data data/data_final.xlsx --figures figures --output output
```

Outputs:
- `figures/` - Figures 1-6, S1 and S2 (PNG at 300 dpi + editable SVG)
- `output/Table_S1_included_studies.xlsx` - all included publications with
  standardised fields
- `output/mapping_review.xlsx` - every mapping decision (algorithm synonyms
  and categories, diseases, metrics) for manual checking

Figure 3 downloads the Natural Earth country boundaries at runtime, so an
internet connection is required.

The original extracted dataset and the generated figures/tables are not part
of this repository; they are published with the article.

## Method

- **Counting unit:** the publication. A publication counts once for every
  algorithm, category, disease or country it covers, so totals can exceed the
  number of studies. Reviews are excluded from all figures.
- **Algorithms:** F2 names are standardised with explicit synonym rules
  (spelling variants, variants of one algorithm, deep-learning architectures
  merged into families) and assigned to categories (F1), which are grouped
  into five method families. All rules are in `src/mappings.py`.
- **Diseases:** WOAH-listed viral diseases only; HPAI, LPAI and unspecified
  avian influenza are merged as AI. Diseases are grouped by main host.
- **Geography:** country of data origin, not author affiliation.
  Continental studies count for every country of the continent; global
  studies are reported in a note, not mapped.

## Figures

1. **Temporal trend** - publications per year, stacked by algorithm category
2. **Machine-learning methods** - (A) categories by method family,
   (B) algorithms used in ≥ 2 publications, (C) category × modelling target
3. **Geography and diseases** - (A) map of data origin, (B) publications per
   disease by host group
4. **Algorithm category × disease** heatmap
5. **Disease × stage and theme** bubble matrix (empty cells = research gaps)
6. **Reported model performance** - AUC and accuracy ranges; validation
   scheme and reporting checklist when the optional columns are present
- **S1.** Publications per country
- **S2.** Co-occurrence of algorithm categories

All figures use one fixed colour per algorithm category and per host group.

## Project Structure

```
├── main.py                     # Pipeline entry point
├── src/
│   ├── data_loading.py         # Loading, cleaning, list parsing, QA report
│   ├── mappings.py             # All standardisation dictionaries
│   ├── plot_style.py           # Shared style, colours and ordering
│   ├── fig_trend.py            # Figure 1
│   ├── fig_algorithms.py       # Figure 2
│   ├── fig_geography.py        # Figure 3 and S1
│   ├── fig_diseases.py         # Figure 4
│   ├── fig_disease_context.py  # Figure 5
│   ├── fig_performance.py      # Figure 6
│   ├── fig_cooccurrence.py     # Figure S2
│   └── tables.py               # Table S1 and mapping QA workbook
├── template/
│   ├── data_template.xlsx      # Example input with the expected columns
│   └── README.md               # Column schema and coding rules
├── data/                       # Place input data here (not tracked)
├── requirements.txt
├── CITATION.cff
└── LICENSE
```

## Citation

If you use this code, please cite:

Szymankiewicz, K. (2026). MLEpiVet-ScR: data processing and visualization pipeline for a scoping review of machine learning in notifiable animal disease epidemiology (Version 2.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23040937

The DOI above (concept DOI) always resolves to the latest version; the DOI of
each specific version is listed on the Zenodo record. Version 1.0.0:
https://doi.org/10.5281/zenodo.23040938

Citation metadata are also provided in [CITATION.cff](CITATION.cff).

## License

MIT - see [LICENSE](LICENSE)

## Author

Krzesimir Szymankiewicz ([ORCID 0009-0008-9844-4019](https://orcid.org/0009-0008-9844-4019))
Research Officer, Department of Virology and Viral Animal Diseases
National Veterinary Research Institute (PIWet-PIB), Puławy, Poland