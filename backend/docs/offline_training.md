# Offline Model Training Guide

## Problem
The current training notebook requires internet access to download datasets from GitHub.

## Solution: Pre-download Training Data

### Step 1: Download Datasets (On Connected System)

```bash
# Download LogHub datasets
mkdir -p training_data
cd training_data

wget https://raw.githubusercontent.com/logpai/loghub/master/HDFS/HDFS_2k.log_structured.csv
wget https://raw.githubusercontent.com/logpai/loghub/master/BGL/BGL_2k.log_structured.csv
wget https://raw.githubusercontent.com/logpai/loghub/master/Thunderbird/Thunderbird_2k.log_structured.csv
wget https://raw.githubusercontent.com/logpai/loghub/master/Mac/Mac_2k.log_structured.csv
wget https://raw.githubusercontent.com/logpai/loghub/master/Windows/Windows_2k.log_structured.csv
wget https://raw.githubusercontent.com/logpai/loghub/master/Linux/Linux_2k.log_structured.csv
```

### Step 2: Transfer to Air-Gapped System

1. Copy `training_data/` folder to encrypted USB drive
2. Transfer to isolated system
3. Mount USB and copy to local storage

### Step 3: Modify Training Script

```python
# Update CONFIG in training notebook
CONFIG = {
    'datasets': [
        '/path/to/training_data/HDFS_2k.log_structured.csv',
        '/path/to/training_data/BGL_2k.log_structured.csv',
        # ... local paths only
    ],
}
```

### Step 4: Train Offline

```python
# Run training completely offline
python train_model.py --offline --data-dir /path/to/training_data
```

### Step 5: Deploy Models

```bash
# Copy trained models to backend
cp iforest_model.pkl backend/data/models/
cp tfidf_vectorizer.pkl backend/data/models/
```
