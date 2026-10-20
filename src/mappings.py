"""
Explicit, reviewable mappings for data_final.xlsx.

Every correction applied to the extracted data lives here as a plain
dictionary, so the published code documents exactly what was merged,
renamed or dropped. Nothing is matched by substring: a value that is not
listed is reported by the QA step instead of being silently guessed.
"""

# ============================================================================
# F1 - algorithm categories (column Cat_Algorithms)
# ============================================================================

# Typos / inconsistent labels in Cat_Algorithms.
CATEGORY_FIXES = {
    'Linear Mode': 'Linear Model',
    'Other (Bayesian Network)': 'Bayesian Network',
    'Other (Fuzzy Time Series, ARIMA)': 'Time Series',
}

# Category order used in every figure (most frequent first) and the
# categories that share the grey "Other" colour because they occur in
# only one or two publications.
CATEGORY_ORDER = [
    'Tree Ensemble', 'Linear Model', 'SVM', 'Neural Network', 'Single Tree',
    'Deep Learning', 'Unsupervised', 'Presence-only SDM', 'kNN', 'Naive Bayes',
]
RARE_CATEGORIES = {'Domain Adaptation', 'Bayesian Network', 'Time Series'}
OTHER_CATEGORY = 'Other'

# Pastel palette carried over from the previous figure set.
CATEGORY_COLORS = {
    'Tree Ensemble': '#A8D8EA',
    'Linear Model': '#FFB3B3',
    'SVM': '#B4E7B3',
    'Neural Network': '#FFE5B4',
    'Single Tree': '#D4A5D4',
    'Deep Learning': '#C9E4CA',
    'Unsupervised': '#FFD4D4',
    'Presence-only SDM': '#FFC9B3',
    'kNN': '#E8D4F1',
    'Naive Bayes': '#F5D5A8',
    OTHER_CATEGORY: '#D3D3D3',
}

# Top level of the hierarchy (family -> F1), used to group and order
# categories in figures and legends. Families are presentational groupings
# by model family, not a strict learning-paradigm taxonomy.
CATEGORY_FAMILIES = {
    'Classical supervised learning': [
        'Tree Ensemble', 'Linear Model', 'SVM', 'Single Tree', 'kNN'],
    'Neural networks and deep learning': ['Neural Network', 'Deep Learning'],
    'Probabilistic models': ['Naive Bayes', 'Bayesian Network'],
    'Unsupervised learning': ['Unsupervised'],
    'Domain-specific methods': ['Presence-only SDM', 'Time Series', 'Domain Adaptation'],
}
CATEGORY_FAMILY = {cat: fam for fam, cats in CATEGORY_FAMILIES.items() for cat in cats}

REVIEW_LABELS = {'Review', 'none', 'Methodology'}

# ============================================================================
# F2 - individual algorithms (column Algorithms)
# ============================================================================

# F2 is the algorithm, not its implementation. Merged here:
#   1. spelling variants;
#   2. variants of one algorithm (kernel, regularisation, link function,
#      version, package-specific name, e.g. biomod2 CTA = rpart = CART);
#   3. named deep architectures into their family (CNN, RNN, GNN,
#      Transformer, YOLO).
# Applied per publication, so a paper listing both "SVM (RBF)" and
# "SVM (linear)" still counts once for Support Vector Machine.
ALGORITHM_SYNONYMS = {
    # 1. spelling variants
    'Multi-Layer Perceptron': 'Multilayer Perceptron',
    'K-Nearest Neighbours': 'k-Nearest Neighbors',
    'K-means Clustering': 'K-means',
    'Multiple Adaptive Regression Splines': 'Multivariate Adaptive Regression Splines',
    'Neural Network': 'Artificial Neural Network',
    'Auto-Regressive Integrated Moving Average': 'ARIMA',
    # 2. variants of one algorithm
    'Agglomerative Hierarchical Clustering': 'Hierarchical Clustering',
    'Gradient Boosting': 'Gradient Boosting Machine',
    'Generalized Boosted Model': 'Gradient Boosting Machine',
    'Generalized Boosting Model': 'Gradient Boosting Machine',
    'Stochastic Gradient Boosting (TreeNet)': 'Gradient Boosting Machine',
    'Gradient Boosted Regression Trees': 'Boosted Regression Trees',
    'RUSBoost': 'AdaBoost',
    'Bagged Trees': 'Bagging',
    'Ensemble': 'Voting Ensemble',
    'Soft Voting Ensemble': 'Voting Ensemble',
    'Hard Voting Ensemble': 'Voting Ensemble',
    'Classification Tree Analysis': 'Classification and Regression Tree',
    'Classification Tree': 'Decision Tree',
    'J48 Decision Tree': 'C4.5 Decision Tree',
    'Support Vector Classification': 'Support Vector Machine',
    'Support Vector Classifier': 'Support Vector Machine',
    'Linear Support Vector Classification': 'Support Vector Machine',
    'Support Vector Machine (RBF)': 'Support Vector Machine',
    'Support Vector Machine (linear)': 'Support Vector Machine',
    'Least Squares Support Vector Machine (PSO-optimised)': 'Support Vector Machine',
    'Logistic Regression (L1 lasso)': 'Logistic Regression',
    'Logistic Regression (L2 ridge)': 'Logistic Regression',
    'Bayesian Logistic Regression': 'Logistic Regression',
    'Multinomial Logistic Regression': 'Logistic Regression',
    'Penalized Multinomial Ridge Logistic Regression': 'Logistic Regression',
    'Poisson Regression': 'Generalized Linear Model',
    'Probit Regression': 'Generalized Linear Model',
    'Gaussian Naive Bayes': 'Naive Bayes',
    'Discriminative Multinomial Naive Bayes': 'Naive Bayes',
    'Additive Bayesian Network': 'Bayesian Network',
    'Neural Network Auto-Regressive': 'Artificial Neural Network',
    'Fully-Connected Neural Network': 'Multilayer Perceptron',
    # 3. deep architectures -> family
    'AlexNet (Convolutional Neural Network, transfer learning)': 'Convolutional Neural Network',
    'ResNet50': 'Convolutional Neural Network',
    'VGG16': 'Convolutional Neural Network',
    'MobileNetV3': 'Convolutional Neural Network',
    'Single Shot Detector (SSD)': 'Convolutional Neural Network',
    'EfficientDet': 'Convolutional Neural Network',
    'You Only Look Once v8 (YOLOv8)': 'YOLO',
    'You Only Look Once v11 (YOLOv11)': 'YOLO',
    'YOLOv8': 'YOLO',
    'YOLOv9': 'YOLO',
    'YOLOv10': 'YOLO',
    'YOLOv10-StarScLS (YOLOv10 with StarNet, LSKA and ScConv)': 'YOLO',
    'Long Short-Term Memory': 'Recurrent Neural Network',
    'Long Short-Term Memory Recurrent Neural Network (LSTM-RNN)': 'Recurrent Neural Network',
    'Gated Recurrent Unit': 'Recurrent Neural Network',
    'CNN-LSTM': 'Hybrid CNN-RNN',
    'CNN-GRU': 'Hybrid CNN-RNN',
    'Graph Cross Attention Network (GCAN-Flu)': 'Graph Neural Network',
    'Graph Attention Network v2 (GATv2)': 'Graph Neural Network',
    'GCNII': 'Graph Neural Network',
    'Simple Graph Convolution (SGC)': 'Graph Neural Network',
    'Frequency Adaptive Graph Convolutional Network (FAGCN)': 'Graph Neural Network',
    'GraphSAGE Graph Neural Network': 'Graph Neural Network',
    'DistilBERT': 'Transformer',
    'NLLB-200': 'Transformer',
    'RT-DETR': 'Transformer',
}

# F2 -> F1, following the column definitions of the extraction protocol.
# Used to colour individual algorithms; publication-level F1 counts come
# from Cat_Algorithms itself.
ALGORITHM_CATEGORY = {
    # Tree Ensemble
    'Random Forest': 'Tree Ensemble',
    'XGBoost': 'Tree Ensemble',
    'Gradient Boosting Machine': 'Tree Ensemble',
    'LightGBM': 'Tree Ensemble',
    'AdaBoost': 'Tree Ensemble',
    'Boosted Regression Trees': 'Tree Ensemble',
    'Bayesian Additive Regression Trees': 'Tree Ensemble',
    'Bagging': 'Tree Ensemble',
    'RuleFit': 'Tree Ensemble',
    # Single Tree
    'Classification and Regression Tree': 'Single Tree',
    'Decision Tree': 'Single Tree',
    'C4.5 Decision Tree': 'Single Tree',
    'Best-First Decision Tree': 'Single Tree',
    'Chi-squared Automatic Interaction Detection': 'Single Tree',
    'Logistic Model Tree': 'Single Tree',
    'Random Tree': 'Single Tree',
    # Linear Model
    'Logistic Regression': 'Linear Model',
    'Generalized Linear Model': 'Linear Model',
    'Generalized Additive Model': 'Linear Model',
    'Multivariate Adaptive Regression Splines': 'Linear Model',
    'Flexible Discriminant Analysis': 'Linear Model',
    'LASSO Regression': 'Linear Model',
    'Linear Regression': 'Linear Model',
    # SVM
    'Support Vector Machine': 'SVM',
    # kNN
    'k-Nearest Neighbors': 'kNN',
    'Kstar': 'kNN',
    # Naive Bayes
    'Naive Bayes': 'Naive Bayes',
    # Neural Network (shallow)
    'Artificial Neural Network': 'Neural Network',
    'Word2Vec': 'Neural Network',
    # Deep Learning
    'Multilayer Perceptron': 'Deep Learning',
    'Deep Learning': 'Deep Learning',
    'Convolutional Neural Network': 'Deep Learning',
    'Recurrent Neural Network': 'Deep Learning',
    'Autoencoder': 'Deep Learning',
    'Transformer': 'Deep Learning',
    'AlexNet': 'Deep Learning',
    'YOLOv11': 'Deep Learning',
    'DeepWalk': 'Deep Learning',
    'YOLO': 'Deep Learning',
    'Hybrid CNN-RNN': 'Deep Learning',
    'Graph Neural Network': 'Deep Learning',
    'Voting Ensemble': 'Tree Ensemble',
    'HostNet': 'Deep Learning',
    'VIDHOP': 'Deep Learning',
    'CCSI-DL': 'Deep Learning',
    # Unsupervised
    'Principal Component Analysis': 'Unsupervised',
    'K-means': 'Unsupervised',
    'Hierarchical Clustering': 'Unsupervised',
    'ST-DBSCAN': 'Unsupervised',
    'FP-Growth': 'Unsupervised',
    'PrefixSpan': 'Unsupervised',
    'Non-metric Multidimensional Scaling': 'Unsupervised',
    'Pointwise Mutual Information': 'Unsupervised',
    'Dice Coefficient': 'Unsupervised',
    'Seasonal Hybrid ESD': 'Unsupervised',
    # Presence-only SDM
    'Maximum Entropy': 'Presence-only SDM',
    'Surface Range Envelope': 'Presence-only SDM',
    'Domain': 'Presence-only SDM',
    # Domain Adaptation
    'Calibrated Uncertainty Prediction': 'Domain Adaptation',
    'Dynamic Weighted Learning': 'Domain Adaptation',
    'Select TARgets': 'Domain Adaptation',
    'Less Annotated Active Learning Extreme Learning Machine': 'Domain Adaptation',
    'Regularized Learning under Label Shifts': 'Domain Adaptation',
    # Other
    'Bayesian Network': 'Bayesian Network',
    'ARIMA': 'Time Series',
    'Fuzzy Time Series (Abbasov-Mamedova)': 'Time Series',
}

# ============================================================================
# Diseases (column Diseases) - WOAH-listed viral diseases only
# ============================================================================

# Raw label -> figure label. Labels not listed here (non-WOAH or
# non-viral diseases) are dropped from disease-level figures.
DISEASE_MAP = {
    # Avian influenza: HPAI, LPAI and unspecified AI merged
    'HPAI': 'AI',
    'LPAI': 'AI',
    'Avian Influenza': 'AI',
    'Low Pathogenic Avian Influenza (H9N2)': 'AI',
    'Low-pathogenic Avian Influenza': 'AI',
    'Low-pathogenic Avian Influenza H9N2': 'AI',
    'Notifiable low-pathogenic H5 and H7 Avian Influenza': 'AI',
    'ASF': 'ASF',
    'FMD': 'FMD',
    'West Nile Fever': 'WNF',
    'WNV': 'WNF',
    'BTV': 'BTV',
    'Newcastle Disease': 'ND',
    'AHS': 'AHS',
    'LSD': 'LSD',
    'CSF': 'CSF',
    'Classical Swine Fever': 'CSF',
    'PRRS': 'PRRS',
    'PPR': 'PPR',
    'EHD': 'EHD',
    'Infectious Bronchitis': 'IB',
    'Infectious Bursal Disease': 'IBD',
    'Avian Infectious Laryngotracheitis': 'ILT',
    'Aujeszky’s Disease': 'AD',
    'Equine Influenza': 'EI',
    'Japanese Encephalitis': 'JE',
    'Rift Valley Fever': 'RVF',
    'Crimean-Congo Haemorrhagic Fever': 'CCHF',
    'Rabies': 'Rabies',
    'Nipah Virus Infection': 'Nipah',
}

# Raw labels deliberately excluded (not WOAH-listed, not viral, or not a
# specific disease). Listed so the QA step can tell "excluded on purpose"
# apart from "unknown label".
DISEASE_EXCLUDED = {
    'Swine Influenza', 'Swine Influenza A', 'Canine Influenza', 'Human Influenza',
    'Zoonotic Influenza A', 'Schmallenberg Disease', 'Schmallenberg Virus',
    'Porcine Epidemic Diarrhoea', 'Porcine Circovirus-Associated Disease',
    'Mycoplasma hyopneumoniae', 'Enzootic Pneumonia', 'Porcine Pleuropneumonia',
    'Infectious Coryza', 'Bovine Tuberculosis', 'Brucellosis', 'Q Fever',
    'Anthrax', 'Salmonellosis', 'Campylobacteriosis', 'Listeriosis',
    'Anaplasmosis', 'Babesiosis', 'Bovine Respiratory Disease',
    'Infectious Bovine Keratoconjunctivitis', 'Liver Abscess', 'Heat Stress',
}

DISEASE_FULL_NAMES = {
    'AI': 'Avian influenza (HPAI, LPAI, unspecified)',
    'ASF': 'African swine fever',
    'FMD': 'Foot-and-mouth disease',
    'WNF': 'West Nile fever',
    'BTV': 'Bluetongue',
    'ND': 'Newcastle disease',
    'AHS': 'African horse sickness',
    'LSD': 'Lumpy skin disease',
    'CSF': 'Classical swine fever',
    'PRRS': 'Porcine reproductive and respiratory syndrome',
    'PPR': 'Peste des petits ruminants',
    'EHD': 'Epizootic haemorrhagic disease',
    'IB': 'Avian infectious bronchitis',
    'IBD': 'Infectious bursal disease',
    'ILT': 'Avian infectious laryngotracheitis',
    'AD': "Aujeszky's disease",
    'EI': 'Equine influenza',
    'JE': 'Japanese encephalitis',
    'RVF': 'Rift Valley fever',
    'CCHF': 'Crimean-Congo haemorrhagic fever',
    'Rabies': 'Rabies',
    'Nipah': 'Nipah virus encephalitis',
}

# Diseases grouped by main host for Figure 4.
DISEASE_HOST_GROUPS = {
    'Poultry': ['AI', 'ND', 'IB', 'IBD', 'ILT'],
    'Swine': ['ASF', 'CSF', 'PRRS', 'AD'],
    'Ruminants': ['FMD', 'BTV', 'LSD', 'PPR', 'EHD'],
    'Equids': ['AHS', 'EI'],
    'Multi-host / zoonotic': ['WNF', 'JE', 'RVF', 'CCHF', 'Rabies', 'Nipah'],
}

# ============================================================================
# Modelling target (column Target) - grouped for Figure 2C
# ============================================================================

TARGET_GROUPS = {
    'Disease occurrence – animal': 'Disease in animals',
    'Disease count – animal': 'Disease in animals',
    'Infection status – individual animal': 'Individual animal / laboratory',
    'Laboratory/diagnostic outcome': 'Individual animal / laboratory',
    'Disease occurrence – human': 'Disease in humans',
    'Disease count – human': 'Disease in humans',
    'Vector occurrence/abundance': 'Vectors and hosts',
    'Vector infection (pathogen detection in vector)': 'Vectors and hosts',
    'Host occurrence/abundance': 'Vectors and hosts',
    'Sequence-based viral trait': 'Viral sequence traits',
    'Animal movement / contact network': 'Other',
    'Stakeholder opinion': 'Other',
    'Intervention uptake': 'Other',
    'No disease target': 'Other',
}
TARGET_GROUP_ORDER = [
    'Disease in animals', 'Individual animal / laboratory', 'Vectors and hosts',
    'Disease in humans', 'Viral sequence traits', 'Other',
]

# ============================================================================
# Countries and regions (column Countries)
# ============================================================================

# Region labels expand to every country of that continent (Natural Earth
# CONTINENT field) on the coverage map; 'Global' expands to all countries.
REGION_CONTINENTS = {
    'Global': None,
    'Europe': 'Europe',
    'Asia': 'Asia',
    'Africa': 'Africa',
}

# Dataset country name -> Natural Earth ADMIN name, where they differ.
COUNTRY_TO_NATURAL_EARTH = {
    'USA': 'United States of America',
}

# ============================================================================
# Performance metrics (column Main_Metric_Type)
# ============================================================================

METRIC_SYNONYMS = {
    'AUROC': 'AUC',
    'AUC (calibrated, AUCc)': 'AUC',
    'R2': 'R²',
}
