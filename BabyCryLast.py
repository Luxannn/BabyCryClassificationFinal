import gradio as gr
import numpy as np
import librosa
import tensorflow as tf
import pickle

# ======================================================================================
# 1) BABY CRY CLASSIFIER
# ======================================================================================
labels = pickle.load(open("label_classes.pkl", "rb"))

def build_babycry_model(num_classes=8):
    inputs = tf.keras.layers.Input(shape=(128, 128, 1))
    x = tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu")(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(2)(x)

    x = tf.keras.layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(2)(x)

    x = tf.keras.layers.Conv2D(256, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(2)(x)

    t = x.shape[1] * x.shape[2]
    c = x.shape[3]
    x = tf.keras.layers.Reshape((int(t), int(c)))(x)

    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True))(x)
    att = tf.keras.layers.Dense(1, activation="tanh")(x)
    att = tf.keras.layers.Softmax(axis=1)(att)
    x = tf.keras.layers.Multiply()([x, att])
    x = tf.keras.layers.Lambda(lambda z: tf.reduce_sum(z, axis=1))(x)

    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    return tf.keras.Model(inputs, outputs)

model = build_babycry_model(num_classes=len(labels))
model.load_weights("BabyCry_CRNN_Attention_FinalLast.weights.h5")
print("✅ BabyCry model loaded successfully!")


# ======================================================================================
# 2) AUTISM / ANOMALY DETECTOR
# ======================================================================================
SR = 16000
FRAME = 1024
HOP = 256
F0_MIN, F0_MAX, HYPER_F0 = 100, 800, 1000

autism_bundle = pickle.load(open("autism_anomaly_ocsvm.pkl", "rb"))
autism_pipeline = autism_bundle["pipeline"]
autism_feature_cols = autism_bundle["features"]
print("✅ Autism anomaly model loaded successfully!")

def compute_f0_features(y, sr=SR):
    f0, _, _ = librosa.pyin(y, fmin=F0_MIN, fmax=F0_MAX, sr=sr, frame_length=FRAME, hop_length=HOP)
    if f0 is None:
        return dict.fromkeys(['f0_mean','f0_std','f0_median','f0_iqr','f0_cv',
                              'f0_jitter','f0_voiced_ratio','f0_hyper_ratio'], 0.0)
    valid = ~np.isnan(f0)
    f0_v = f0[valid]
    if len(f0_v) == 0:
        return dict.fromkeys(['f0_mean','f0_std','f0_median','f0_iqr','f0_cv',
                              'f0_jitter','f0_voiced_ratio','f0_hyper_ratio'], 0.0)
    f0_mean = np.mean(f0_v)
    f0_std = np.std(f0_v)
    f0_median = np.median(f0_v)
    q1, q3 = np.percentile(f0_v, [25, 75])
    f0_iqr = q3 - q1
    f0_cv = f0_std / (f0_mean + 1e-9)
    T = 1.0 / (f0_v + 1e-9)
    jitter = np.mean(np.abs(np.diff(T))) / (np.mean(T) + 1e-9) if len(T) > 1 else 0.0
    voiced_ratio = np.mean(valid)
    hyper_ratio = np.mean(f0_v > min(HYPER_F0, F0_MAX))
    return dict(f0_mean=f0_mean, f0_std=f0_std, f0_median=f0_median,
                f0_iqr=f0_iqr, f0_cv=f0_cv, f0_jitter=jitter,
                f0_voiced_ratio=voiced_ratio, f0_hyper_ratio=hyper_ratio)

def compute_energy_pause_features(y):
    rms = librosa.feature.rms(y=y, frame_length=FRAME, hop_length=HOP)[0]
    rms_mean = np.mean(rms)
    rms_std = np.std(rms)
    rms_cv = rms_std / (rms_mean + 1e-9)
    thr = np.median(rms) * 0.6
    silence_ratio = np.mean(rms < thr)
    return dict(rms_mean=rms_mean, rms_std=rms_std, rms_cv=rms_cv, silence_ratio=silence_ratio)

def compute_spectral_features(y, sr=SR):
    S = np.abs(librosa.stft(y, n_fft=FRAME, hop_length=HOP))
    sc = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
    sc_mean, sc_std = np.mean(sc), np.std(sc)
    sc_cv = sc_std / (sc_mean + 1e-9)
    flatness = librosa.feature.spectral_flatness(S=S)[0]
    flat_mean, flat_std = np.mean(flatness), np.std(flatness)
    harm = librosa.effects.harmonic(y)
    noise = y - harm
    hnr = (np.mean(np.abs(harm)) + 1e-9) / (np.mean(np.abs(noise)) + 1e-9)
    return dict(sc_mean=sc_mean, sc_std=sc_std, sc_cv=sc_cv,
                flat_mean=flat_mean, flat_std=flat_std, hnr=hnr)

def lpc_formants(y, sr=SR, lpc_order=12):
    y2 = librosa.effects.preemphasis(y)
    rms = librosa.feature.rms(y=y2, frame_length=FRAME, hop_length=HOP)[0]
    idx = np.argmax(rms)
    start = max(0, idx * HOP - FRAME)
    seg = y2[start:start + 4*FRAME]
    if len(seg) < 2*FRAME:
        seg = np.pad(seg, (0, 2*FRAME - len(seg)))
    try:
        a = librosa.lpc(seg, order=lpc_order)
        roots = np.roots(a)
        roots = roots[np.imag(roots) >= 0.01]
        ang = np.arctan2(np.imag(roots), np.real(roots))
        freqs = np.sort(ang * (sr / (2*np.pi)))
        freqs = freqs[(freqs > 90) & (freqs < 5000)]
        F1 = freqs[0] if len(freqs) > 0 else 0.0
        F2 = freqs[1] if len(freqs) > 1 else 0.0
    except Exception:
        F1, F2 = 0.0, 0.0
    return dict(F1=F1, F2=F2)

def extract_all_features_vector(y):
    f = {}
    f.update(compute_f0_features(y, SR))
    f.update(compute_energy_pause_features(y))
    f.update(compute_spectral_features(y, SR))
    f.update(lpc_formants(y, SR))
    return np.array([f[c] if c in f else 0.0 for c in autism_feature_cols],
                    dtype=np.float32).reshape(1, -1)


# ======================================================================================
# 3) PREDICTION LOGIC
# ======================================================================================
def extract_logmel(y, sr):
    y = y[:int(2.5 * sr)]
    if len(y) < int(2.5 * sr):
        y = np.pad(y, (0, int(2.5 * sr) - len(y)))
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, hop_length=512)
    logmel = librosa.power_to_db(mel, ref=np.max)
    logmel = librosa.util.fix_length(logmel, size=128, axis=1)
    logmel = (logmel - np.mean(logmel)) / (np.std(logmel) + 1e-9)
    return logmel[np.newaxis, ..., np.newaxis]

def analyze(audio):
    if audio is None:
        return "No audio uploaded."

    try:
        y, sr = librosa.load(audio, sr=16000)

        # Silence filter
        rms = np.mean(librosa.feature.rms(y=y))
        if rms < 0.005:
            return "🟦 No cry detected (silence/background)."

        # Cry-structure filter
        f0, _, _ = librosa.pyin(y, fmin=200, fmax=800, sr=sr)
        voiced_ratio = np.mean(~np.isnan(f0))
        if voiced_ratio < 0.2:
            return "🟨 No cry pattern detected (non-cry sound)."

        # Baby cry classification
        feat = extract_logmel(y, sr)
        pred = model.predict(feat, verbose=0)[0]
        label = labels[np.argmax(pred)]

        # Autism anomaly detection
        acoustic_feat = extract_all_features_vector(y)
        anomaly_score = autism_pipeline.predict(acoustic_feat)[0]

        if anomaly_score == -1:
            return f"🔴 Detected: {label}\n⚠️ Atypical cry pattern (possible developmental anomaly)."
        else:
            return f"🟩 Detected: {label}\n✅ Typical cry pattern."

    except Exception as e:
        return f"Error: {str(e)}"


# ======================================================================================
# 4) GRADIO UI
# ======================================================================================
demo = gr.Interface(
    fn=analyze,
    inputs=gr.Audio(sources=["upload", "microphone"], type="filepath", label="Upload or Record Baby Cry"),
    outputs=gr.Textbox(label="Analysis Result"),
    title="👶 Baby Cry Analyzer",
    description="Upload or record a baby's cry to classify emotional state and detect possible atypical cry patterns."
)

demo.launch()
