# MLEpiVet-ScR

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23040937.svg)](https://doi.org/10.5281/zenodo.23040937)

**Data processing and visualization pipeline for a scoping review of machine learning in notifiable animal disease epidemiology**

Analysis code for the PRISMA-ScR scoping review: "Application of Machine Learning Methods in the Epidemiology of Notifiable Animal Diseases"

## Overview

This repository contains Python scripts for data cleaning, standardization, and figure generation for a scoping review covering eight WOAH-notifiable diseases (ASF, FMD, HPAI, BTV, CSF, ND, LSD, WNV).

**Master bibliography:** 384 unique records (164 included after exclusions)
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

Copy `template/data_template.xlsx` to `data/data_ml_publications.xlsx` and
replace the example rows with your own extracted records (see
`template/README.md` for the column schema), then run:

```bash
python main.py
```

This will generate:
- publication-ready figures (PNG + SVG) in `figures/`
- Table S2 complete bibliography (Excel), a disease summary table
  (CSV/JSON/Markdown/Excel) and a standardized-data preview for QA in `output/`

Figure 3b downloads the Natural Earth country boundaries at runtime, so an
internet connection is required.

The original extracted dataset and the generated figures/tables are not part
of this repository; they are published with the article.

## Figures

1. **Temporal trend** (2016-2026) by Section
2. **Algorithm vs Disease** heatmap
3. **Top countries** (horizontal bar)
   - **3b. Geographic distribution** (choropleth map)
4. **Top 15 algorithms** (horizontal bar)
5. **Publication distribution** by Stage (pie/donut)

All figures: 300 DPI, Arial font, white background.

## Project Structure

```
├── main.py                          # Pipeline entry point
├── src/
│   ├── data_cleaning.py             # Loading data, removing excluded records
│   ├── standardization.py           # Disease/algorithm/country/stage standardization
│   ├── standardization_mappings.py  # Mapping rules to standard categories
│   ├── figure_generator.py          # Figures 1-5
│   ├── table_generator.py           # Table S2, standardized-data preview
│   └── disease_summary.py           # Per-disease summary table
├── template/
│   ├── data_template.xlsx           # Example input with the expected columns
│   └── README.md                    # Column schema
├── data/                            # Place input data here (not tracked)
├── requirements.txt
├── CITATION.cff
└── LICENSE
```

## Citation

If you use this code, please cite:

Szymankiewicz, K. (2026). MLEpiVet-ScR: data processing and visualization pipeline for a scoping review of machine learning in notifiable animal disease epidemiology (Version 1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23040938

To cite all versions, use the concept DOI: https://doi.org/10.5281/zenodo.23040937

Citation metadata are also provided in [CITATION.cff](CITATION.cff).

## License

MIT - see [LICENSE](LICENSE)

## Author

Krzesimir Szymankiewicz ([ORCID 0009-0008-9844-4019](https://orcid.org/0009-0008-9844-4019))
Research Officer, Department of Virology and Viral Animal Diseases
National Veterinary Research Institute (PIWet-PIB), Puławy, Poland