import streamlit as st
import numpy as np
import pyaudio
import wave
import pickle
import librosa
from sklearn.ensemble import RandomForestClassifier

# Боргирии модели омӯзонидашуда
pickle_in = open("BabyCryModel.pkl", "rb")
model = pickle.load(pickle_in)

# Луғат барои тарҷумаи натиҷаҳо
prediction_translation = {
    "hungry": "Гурусна",
    "sleepy": "Хоболуд",
    "discomfort": "Ноором",
    "pain": "Дарднок",
    "attention": "Таваҷҷӯҳ мехоҳад"
}

# **Танзимоти Streamlit**
st.set_page_config(page_title="Пешгӯии гиряи кӯдак", layout="wide")

# **CSS барои беҳбуди интерфейс**
st.markdown("""
    <style>
        /* Заминаи сафед */
        body, .stApp {background-color: white !important;}

        /* Унвонҳо ва матнҳо */
        .title {color: #1E3A8A; font-size: 32px; font-weight: bold; text-align: center;}
        .subtitle {color: #444; font-size: 18px; text-align: center;}

        /* Сабти аудио */
        .recording {font-size: 20px; font-weight: bold; color: #D84315; text-align: center;}

        /* Қуттии пешгӯӣ */
        .prediction-box {
            background-color: #E3F2FD; 
            padding: 15px; 
            border-radius: 10px; 
            font-size: 20px; 
            font-weight: bold; 
            text-align: center; 
            border: 2px solid #1E88E5; 
            color: #0D47A1;
        }

        /* Тугма */
        .stButton>button {
            font-size: 18px; 
            padding: 12px; 
            background-color: #1E88E5; 
            color: white; 
            border-radius: 10px; 
            width: 100%; 
            border: none;
        }
        .stButton>button:hover {background-color: #1565C0;}

        /* Қисми поёнӣ */
        .footer {color: gray; font-size: 14px; text-align: center; margin-top: 30px;}
    </style>
""", unsafe_allow_html=True)

# **Унвони асосӣ**
st.markdown("<div class='title'>🔊 Пешгӯии гиряи кӯдак</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Ин асбоб ҳолати эҳсосии кӯдакро аз рӯи овози гиряи ӯ муайян мекунад.</div>", unsafe_allow_html=True)

# **Тугма барои сабти овоз**
st.markdown("### 🎙 Сабти овозро оғоз кунед")
start_button = st.button("🎤 Оғози сабт")

# Сабт ва коркарди аудио
if start_button:
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    audio_frames = []
    st.markdown("<div class='recording'>🔴 Сабт оғоз шуд... Лутфан, садои гиряи кӯдакро садо диҳед.</div>", unsafe_allow_html=True)

    for _ in range(0, int(44100 / 1024 * 5)):  # Сабти 5 сония
        audio_data = stream.read(1024)
        audio_frames.append(audio_data)

    st.success("✅ Сабт анҷом ёфт.")
    p.terminate()

    with wave.open("recorded_audio.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b"".join(audio_frames))

    # Коркарди аудио ва пешгӯии натиҷа
    try:
        audio_path = "recorded_audio.wav"
        
        with wave.open(audio_path, 'rb') as audio_file:
            audio_data = audio_file.readframes(-1)
            sr = audio_file.getframerate()
            audio = np.frombuffer(audio_data, dtype=np.int16)
        
        audio = audio.astype(np.float64)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr)
        mfccs_mean = np.mean(mfccs, axis=1)

        prediction = model.predict([mfccs_mean])[0]
        predicted_label = prediction_translation.get(prediction)

        st.markdown("### 📌 Натиҷаи пешгӯӣ")
        st.markdown(f"<div class='prediction-box'>🍼 Гиряи кӯдак эҳтимолан: <b>{predicted_label}</b></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Хато ҳангоми коркарди аудио: {str(e)}")

# **Қисми поёнӣ бо маълумоти муаллифӣ**
st.markdown("<div class='footer'>© Ҳамаи ҳуқуқҳо ҳифз шудаанд - <b>Mercurii.AI</b></div>", unsafe_allow_html=True)
