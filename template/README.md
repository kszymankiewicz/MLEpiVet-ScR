# Data template

`data_template.xlsx` shows the column schema the pipeline expects (three
fictional example rows). To run the pipeline on your own review data:

1. Copy `template/data_template.xlsx` to `data/data_final.xlsx`.
2. Replace the example rows with your own extracted records.
3. Run `python main.py` from the project root.

Multi-valued cells are separated with `"; "` (semicolon + space). Leading or
trailing spaces and tabs are removed automatically. Spelling variants,
synonyms and category assignments are handled by the explicit dictionaries in
`src/mappings.py`; `output/mapping_review.xlsx` lists every mapping decision
and any value the dictionaries do not recognise.

## Required columns

| Column | Content |
|---|---|
| `ID` | Unique record number |
| `Authors` | `Surname Given-name`, comma-separated, in publication order |
| `Year` | Publication year (integer) |
| `Title` | Full title |
| `DOI` | DOI without `https://doi.org/` |
| `Journal` | Full journal name |
| `Cat_Algorithms` | Algorithm categories (F1), e.g. `Tree Ensemble; Linear Model`. Kept for QA only: figures derive F1 from `Algorithms` via `ALGORITHM_CATEGORY` |
| `Algorithms` | Algorithms (F2) actually used, full names, e.g. `Random Forest; XGBoost`. `Review` for reviews |
| `Countries` | Countries the data come from (not author affiliation). `Global` or continent names (`Europe`, `Asia`, `Africa`) for multi-country scope |
| `Diseases` | Diseases studied. Only WOAH-listed viral diseases in `DISEASE_MAP` enter disease figures |
| `Stage` | One of: `Prediction/Forecasting`, `Surveillance`, `Diagnostics`, `Field`, `Methodology/Review`, `Other`. `Methodology/Review` marks a review and excludes the record from all figures |
| `Theme` | One of: `Geospatial & Environmental`, `Emerging Applications and Technologies`, `Methodological Challenges`, `Syndromic Surveillance & NLP`, `Animal Movement & Trade Networks`, `One Health & Future Perspectives` |
| `Target` | Modelling target (see `TARGET_GROUPS` in `src/mappings.py`); two targets joined with ` + ` |
| `Main_Metric_Type` | Main performance metric, e.g. `AUC`, `Accuracy`; `none` if not reported, `Review` for reviews |
| `Main_Metric_Value_min` | Value of the worst reported model (decimal, not %) |
| `Main_Metric_Value_max` | Value of the best reported model (decimal, not %) |
| `Notes` | One or two sentences on aim and main limitation |
| `Sources` | Databases, e.g. `PubMed; Scopus; WoS` |

## Optional reporting-quality columns (Figure 6)

If present, Figure 6 colours studies by validation scheme and adds a
reporting checklist panel (percentages of applicable publications). Code every non-review publication; leave the
cells empty for reviews.

### `Validation` - the most stringent validation of the final model

Choose the highest applicable level: **External > Temporal > Spatial >
Random split/CV > None reported**.

| Value | Code when |
|---|---|
| `External` | Performance is reported on an independent dataset not used in any step of model development (different surveillance system, country, laboratory or study) |
| `Temporal` | The model is trained on an earlier period and tested on a later, held-out period (forecast hold-out, rolling origin) |
| `Spatial` | Test data are geographically separated from training data (spatial block or buffered cross-validation, leave-region-out, held-out areas) |
| `Random split/CV` | Test units are drawn at random from the same data pool: train/test split, k-fold or leave-one-out CV, bootstrap, out-of-bag error |
| `None reported` | Performance only on training data, validation not described, or unsupervised analysis without a validation step |

### `Spatial_blocked`, `Temporal_holdout` - `yes`, `no` or `NA`

Record each design separately, because a study can use both while
`Validation` keeps only the most stringent one.

| Column | `yes` when | `NA` when |
|---|---|---|
| `Spatial_blocked` | Any spatially separated validation is used (spatial block or buffered CV, leave-region-out, held-out areas) | No validation, or data have no spatial dimension |
| `Temporal_holdout` | Any later period is held out for testing (forecast hold-out, rolling origin) | No validation, or data have no time dimension |

### Reporting items - `yes`, `no` or `NA`

`NA` (not applicable) or an empty cell is excluded from the percentage in
Figure 6C.

| Column | `yes` when | `NA` when |
|---|---|---|
| `Reports_AUPRC` | Area under the precision-recall curve or average precision is reported for the main model | Not a binary classification task |
| `Reports_SensSpec` | Sensitivity (recall) and specificity are both reported, or a full confusion matrix is given | Not a classification task |
| `Reports_CI` | An uncertainty interval accompanies the main metric (confidence or credible interval, SD/SE across folds or bootstrap) | No performance metric reported |
| `Reports_Calibration` | Calibration is assessed (calibration plot, Brier score, calibration slope/intercept, Hosmer-Lemeshow) | Model output is not a probability (regression, clustering) |

Rules: use the main text and supplementary material; code what is reported
for the final (selected) model; when unsure, record the reason in `Notes`.
