# Data template

`data_template.xlsx` shows the exact column schema the pipeline expects. To run
the pipeline on your own scoping/systematic review data:

1. Copy `template/data_template.xlsx` to `data/data_ml_publications.xlsx`.
2. Replace the example rows with your own extracted records.
3. Run `python main.py` from the project root.

## Columns

| Column | Description |
|---|---|
| `Authors` | Author list, as free text (e.g. `"Smith J, Doe A"`) |
| `Year` | Publication year (integer) |
| `Title` | Article title |
| `DOI` | DOI string |
| `Journal` | Journal name |
| `Disease` | Disease(s) studied. Comma/semicolon/slash-separated if multiple. Mapped to standard categories (ASF, FMD, HPAI, BTV, CSF, ND, LSD, WNV, General, Zoonotic, AMR, Other) by `src/standardization_mappings.py::map_disease` |
| `Algorithm(s)` | ML algorithm(s) used, comma/semicolon/slash-separated if multiple. Mapped by `map_algorithm` / `map_algorithms_multilabel` |
| `Section` | Free-text application area (used as supplementary detail, not standardized) |
| `Country` | Country/countries studied, comma/semicolon-separated if multiple. Mapped by `map_country` |
| `Main metric` | Reported performance metric (e.g. `"AUC = 0.91"`) - free text, not standardized |
| `Stage` | Application stage, mapped by `map_stage` to (Surveillance, Prediction/Forecasting, Diagnostics, Field, Spatial Modeling, Methodology/Review, Other) |
| `Status` | `included` or `excluded` - only `included` records survive `remove_excluded()` |
| `Notes` | Free-text notes |
| `Sources` | Databases the record was found in, comma-separated (e.g. `"PubMed, Scopus, WoS"`) - used by Figure 1 |

Do not include `*_Standardized` columns - the pipeline computes those itself
and drops any pre-existing ones on load (see `src/data_cleaning.py`).
