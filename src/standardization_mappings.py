"""
Standardization mappings with intelligent substring matching.
"""

import re
import pandas as pd

# ============================================================================
# ALGORITHM MAPPING (multi-label: legacy standalone script parity)
# ============================================================================
# Ported from the original ml_standard.py used for the first-pass
# standardization pass. Checks the *entire* raw Algorithm(s) string against
# every keyword and returns every category that matches anywhere - a
# publication mentioning several algorithms counts toward all of them.
# Feeds Figures 2/4 directly (multi-row expansion) and Table S2 / the QA
# preview (map_algorithm_display below, joined into one display string).

ALGORITHM_STANDARDIZATION_KEY = {
    'Random Forest': ['random forest', 'rf)', 'rf;', 'rf,,', 'rf,', 'rf', 'andom forest'],
    'XGBoost': ['xgboost', 'xgb', 'extreme gradient', 'gradient boost', 'catboost', 'lightgbm', 'brt', 'boosted regression'],
    'Deep Learning': ['lstm', 'cnn', 'rnn', 'gru', 'gat', 'gcn', 'gnn', 'transformer', 'yolo', 'deep', 'neural network', 'autoencoder', 'gan', 'mlp', 'ann', 'dnn', 'bert', 'distilbert', 'yolov', 'retinanet'],
    'SVM': ['support vector', 'svm', 'svc', 'svr'],
    'Spatial/GIS': ['maxent', 'maximum entropy', 'ecological niche', 'kriging', 'gis', 'idw', 'spatial'],
    'Bayesian': ['bayesian', 'naive bayes', 'bayes', 'probabilistic'],
    'NLP': ['nlp', 'text mining', 'word2vec', 'lda', 'natural language', 'llm', 'gpt', 'n-gram'],
    'Logistic Regression': ['logistic regression', 'glm', 'generalized linear', 'lasso', 'ridge', 'lr'],
    'K-Means': ['k-means', 'kmeans', 'hierarchical', 'agglomerative', 'hdbscan'],
    'Decision Tree': ['decision tree', 'cart', 'c4.5', 'classification tree'],
    'Ensemble': ['ensemble', 'adaboost', 'bagging', 'voting', 'stacking', 'rulefit'],
    'KNN': ['k-nearest', 'knn', 'k nearest'],
    'Time Series': ['arima', 'sarima', 'autoregressive', 'holt-winters', 'exponential', 'ma(', 'time series'],
    'Statistical Regression': ['poisson', 'negative binomial', 'glmm', 'gam', 'distributed lag'],
    'Network Analysis': ['network analysis', 'graph neural', 'gnn'],
    'Feature Selection': ['feature selection', 'cfsubseteval', 'bestfirst', 'boruta'],
}

_ALGORITHM_REVERSE_KEY = {
    variant.lower().strip(): standard_name
    for standard_name, variants in ALGORITHM_STANDARDIZATION_KEY.items()
    for variant in variants
}

# Abbreviations too short to safely substring-match (e.g. 'nb' for Naive
# Bayes would also match inside "unbiased", "unbalanced", ...). Matched only
# as a standalone token (split on non-alphanumeric chars) instead.
_TOKEN_ONLY_ALGORITHM_VARIANTS = {
    'nb': 'Bayesian',  # Naive Bayes
}


def map_algorithms_multilabel(raw_algorithm: str) -> list:
    """
    Return every algorithm category mentioned anywhere in raw_algorithm.
    A publication can match several categories at once (multi-label);
    review mentions or values with no keyword match return an empty list.
    """
    if pd.isna(raw_algorithm):
        return []

    if 'review' in str(raw_algorithm).lower():
        return []

    value_str = str(raw_algorithm).lower().replace('/', ', ').replace(';', ',')

    found = set()
    for variant, standard_name in _ALGORITHM_REVERSE_KEY.items():
        if variant in value_str:
            found.add(standard_name)

    tokens = set(re.split(r'[^a-z0-9]+', value_str))
    for token, standard_name in _TOKEN_ONLY_ALGORITHM_VARIANTS.items():
        if token in tokens:
            found.add(standard_name)

    for match in re.finditer(r'\(([^)]+)\)', value_str):
        bracket_text = match.group(1)
        for variant, standard_name in _ALGORITHM_REVERSE_KEY.items():
            if variant in bracket_text:
                found.add(standard_name)

    return sorted(found)


def map_algorithm_display(raw_algorithm: str) -> str:
    """
    Single display string for per-publication views (Table S2, QA preview):
    every algorithm category detected by map_algorithms_multilabel, joined
    with '; '.

    A raw entry can name several distinct algorithms (e.g. "Random Forest
    (RF); Boosted Regression Tree (BRT)", or "GRU; LSTM; CNN-GRU; CNN-LSTM;
    RF; SVM; NB"). Picking a single first-match category for these silently
    drops the others and was also inconsistent with Figures 2/4, which
    already count every category via map_algorithms_multilabel - so this
    reuses that same logic instead of a separate single-label mapping.
    """
    categories = map_algorithms_multilabel(raw_algorithm)
    return '; '.join(categories) if categories else None


# ============================================================================
# DISEASE MAPPING (multi-label: detect every category mentioned, then decide
# how many to keep)
# ============================================================================
# map_disease() used to return a single category via first-match-wins over a
# fixed priority order - so a publication on "Fourteen priority zoonotic
# diseases (including HPAI, West Nile fever, Ebola, ...)" was silently
# reduced to "HPAI" alone, because the HPAI check ran before the Zoonotic
# one, regardless of which category the text was actually about. Replaced
# with the same detect-everything-then-decide approach used for algorithms
# (map_algorithms_multilabel): find every category actually mentioned, then
# apply one explicit rule instead of an accidental one from code order.

DISEASE_STANDARDIZATION_KEY = {
    'ASF': ['asf', 'african swine fever'],
    'FMD': ['fmd', 'foot-and-mouth'],
    'HPAI': ['hpai', 'avian influenza', 'h5n1', 'h7n9', 'h9n2'],
    'BTV': ['btv', 'bluetongue'],
    'CSF': ['csf', 'classical swine fever'],
    'ND': ['newcastle'],
    'LSD': ['lsd', 'lumpy skin'],
    'WNV': ['wnv', 'west nile'],
    'AMR': ['amr', 'antimicrobial resistance', 'carbapenem'],
    'Zoonotic': ['zoonotic', 'pandemic', 'emerging pathogen', 'nipah', 'ebola', 'mers', 'covid'],
    'General': ['multiple', 'general', 'various', 'several'],
}

_DISEASE_REVERSE_KEY = {
    variant.lower().strip(): standard_name
    for standard_name, variants in DISEASE_STANDARDIZATION_KEY.items()
    for variant in variants
}

# Abbreviations too short/ambiguous to substring-match anywhere (e.g. 'nd'
# would also match inside "background", "expand", ...). Matched only as a
# standalone token (split on non-alphanumeric chars), same mechanism as
# _TOKEN_ONLY_ALGORITHM_VARIANTS above.
_TOKEN_ONLY_DISEASE_VARIANTS = {
    'nd': 'ND',    # Newcastle Disease
    'aiv': 'HPAI',  # Avian Influenza Virus
}


def map_diseases_multilabel(raw_disease: str) -> list:
    """Every disease category mentioned anywhere in raw_disease (see
    map_algorithms_multilabel - same design)."""
    if pd.isna(raw_disease):
        return []

    value_str = str(raw_disease).lower()

    found = set()
    for variant, standard_name in _DISEASE_REVERSE_KEY.items():
        if variant in value_str:
            found.add(standard_name)

    tokens = set(re.split(r'[^a-z0-9]+', value_str))
    for token, standard_name in _TOKEN_ONLY_DISEASE_VARIANTS.items():
        if token in tokens:
            found.add(standard_name)

    return sorted(found)


def resolve_disease_categories(raw_disease: str) -> list:
    """
    Decide how to count a publication's disease(s) from the categories
    map_diseases_multilabel() detects:
      - none matched -> ['Other']
      - 1-3 distinct categories -> kept separate, one entry per category
        (a publication on 2-3 named diseases counts toward each of them)
      - 4+ distinct categories -> too diffuse to enumerate, collapsed to
        ['General'] (mirrors the >=3-diseases-collapse rule already used
        for the raw comma-split count elsewhere, just based on distinct
        detected categories instead of raw list length)
    """
    categories = map_diseases_multilabel(raw_disease)
    if not categories:
        return ['Other']
    if len(categories) > 3:
        return ['General']
    return categories


def map_disease_display(raw_disease: str) -> str:
    """Table S2 / single-row display: '; '-joined resolve_disease_categories()."""
    return '; '.join(resolve_disease_categories(raw_disease))


# ============================================================================
# STAGE MAPPING
# ============================================================================

STAGE_CATEGORIES = [
    'Surveillance', 'Prediction/Forecasting', 'Diagnostics',
    'Field', 'Spatial Modeling', 'Methodology/Review', 'Other'
]

def map_stage(raw_stage: str) -> str:
    """Map stage using substring matching."""
    if pd.isna(raw_stage):
        return 'Other'
    
    stage_lower = str(raw_stage).strip().lower()
    
    if any(keyword in stage_lower for keyword in ['surveillance', 'early detection', 'early warning', 'monitoring', 'detection', 'syndromic', 'event-based']):
        return 'Surveillance'
    if any(keyword in stage_lower for keyword in ['prediction', 'forecast', 'risk prediction', 'risk mapping', 'outbreak', 'predict']):
        return 'Prediction/Forecasting'
    if any(keyword in stage_lower for keyword in ['diagnosis', 'diagnostic', 'identification', 'classification', 'screening', 'pathogenicity']):
        return 'Diagnostics'
    if any(keyword in stage_lower for keyword in ['field', 'validation', 'deployment']):
        return 'Field'
    if any(keyword in stage_lower for keyword in ['spatial', 'spatial risk', 'modeling', 'ecological niche', 'habitat suitability']):
        return 'Spatial Modeling'
    if any(keyword in stage_lower for keyword in ['review', 'systematic', 'methodology', 'methodological']):
        return 'Methodology/Review'
    
    return 'Other'


# ============================================================================
# COUNTRY MAPPING (simple)
# ============================================================================

COUNTRY_CATEGORIES = list(set([
    'USA', 'China', 'UK', 'South Korea', 'Canada', 'India', 'Italy',
    'France', 'Spain', 'Australia', 'Japan', 'Thailand', 'Germany',
    'Poland', 'Romania', 'New Zealand', 'International'
]))

COUNTRY_MAPPING_SIMPLE = {
    'USA': 'USA',
    'United States': 'USA',
    'China': 'China',
    'UK': 'UK',
    'United Kingdom': 'UK',
    'South Korea': 'South Korea',
    'Korea': 'South Korea',
    'Canada': 'Canada',
    'India': 'India',
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
    'Eqypt': 'Egypt',  # typo in the source Excel (DOI 10.1038/s41598-025-23846-7)
}

def map_country(raw_country: str) -> str:
    """
    Map country - ROZSZERZ wielokrajowe wpisy zamiast excludować.
    """
    if pd.isna(raw_country):
        return None
    
    country_str = str(raw_country).strip()
    
    # EXCLUDE non-country metadata entries
    exclude_keywords = [
        'global', 'international', 'not applicable', 
        'not country', 'international review', 'international',
        'review', 'from ', 'south america', 'north america',
        'europe', 'asia', 'africa', 'multiple'
    ]
    
    if any(keyword in country_str.lower() for keyword in exclude_keywords):
        return None
    
    # Exact match
    if country_str in COUNTRY_MAPPING_SIMPLE:
        return COUNTRY_MAPPING_SIMPLE[country_str]
    
    # Valid single country - return as-is (expansion będzie zrobiona w expand_multivalued_fields)
    return country_str