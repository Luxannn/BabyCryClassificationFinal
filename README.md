# Baby Cry Classification & Anomaly Detection

An ML tool that classifies infant cries by cause and detects atypical cry patterns that may indicate developmental concerns. Built for low-resource clinical settings where specialist access is limited.

## What It Does

1. **Cry Classification** — Identifies why a baby is crying (hungry, tired, discomfort, etc.) using a CRNN model with attention mechanism (~80% accuracy)
2. **Anomaly Detection** — Flags atypical cry patterns using acoustic analysis and One-Class SVM, which may warrant further evaluation

Tested on 200+ recordings in collaboration with pediatricians in Tajikistan.

## Demo

Run the Gradio interface:

```bash
python BabyCryLast.py
```

Upload or record audio to get:
- Predicted cry category
- Whether the cry pattern is typical or atypical

## Project Structure

```
├── BabyCryLast.py                          # Inference script + Gradio UI
├── BabyCryTHE-FINAL-ONE.ipynb              # Main training notebook
├── baby-cry-FIRST.ipynb                    # Initial experiments
├── BabyCry_CRNN_Attention_FinalLast.weights.h5  # Trained CRNN model weights
├── autism_anomaly_ocsvm.pkl                # Anomaly detector (One-Class SVM pipeline)
├── label_classes.pkl                       # Class label encoder
├── RandomForest_model.pkl                  # Alternative RF model
├── BabyCryModel.pkl                        # Additional model artifact
├── label.joblib                            # Label encoder (joblib format)
├── src/                                    # Source utilities
├── website/                                # Web interface files
└── requirements.txt                        # Dependencies
```

## Installation

```bash
git clone https://github.com/Luxannn/BabyCryClassificationFinal.git
cd BabyCryClassificationFinal
pip install numpy pandas scikit-learn librosa soundfile tensorflow gradio matplotlib
```

## How It Works

### Cry Classifier (CRNN + Attention)

1. Audio resampled to 16kHz, trimmed/padded to 2.5 seconds
2. Log-mel spectrogram extracted (128 mels)
3. CNN layers extract spatial features → Bidirectional LSTM captures temporal patterns → Attention weights highlight important frames
4. Outputs probability distribution over 8 cry categories

### Anomaly Detector (One-Class SVM)

Extracts acoustic features:
- **Pitch (F0):** mean, std, median, IQR, jitter, voiced ratio, hyper-pitch ratio
- **Energy:** RMS mean/std/CV, silence ratio
- **Spectral:** centroid, flatness, harmonic-to-noise ratio
- **Formants:** F1, F2 via LPC analysis

One-Class SVM trained on typical cries flags outliers as potentially atypical.

## Dataset

Dataset not included in this repository. To retrain:

1. Organize audio files by class:
```
data/
  hungry/
  lonely/
  discomfort/
  burping/
  belly_pain/
  tired/
  ...
```

2. Each folder contains `.wav` files (16kHz recommended)
3. Run the training notebook `BabyCryTHE-FINAL-ONE.ipynb`

## Usage

### Gradio Demo (Recommended)

```bash
python BabyCryLast.py
```

### Programmatic

```python
from BabyCryLast import analyze

result = analyze("path/to/baby_cry.wav")
print(result)
# Output: "🟩 Detected: hungry\n✅ Typical cry pattern."
```

## Model Files Required

Ensure these files are in the working directory:
- `BabyCry_CRNN_Attention_FinalLast.weights.h5`
- `autism_anomaly_ocsvm.pkl`
- `label_classes.pkl`

## Author

**Muslim Saidov** — Dushanbe, Tajikistan  
muslim.s.saidov@gmail.com

---
