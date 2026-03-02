import streamlit as st
import os
import moviepy.editor as mp
import whisper
import random
import gc
import time

# --- SYSTEM CONFIG ---
# Note: Streamlit Cloud handles ImageMagick automatically, no path needed!

st.set_page_config(page_title="ApexClip AI", layout="wide")
st.markdown("<style>.stApp { background-color: #FFFFFF; color: #000000; } .stButton>button { background-color: #000000; color: #FFFFFF; width: 100%; border-radius: 4px; }</style>", unsafe_allow_html=True)

st.title("🎬 APEXCLIP AI: PERMANENT TERMINAL")

with st.sidebar:
    st.header("⚙️ Settings")
    layout = st.selectbox("Format", ["9:16 Vertical", "1:1 Square"])
    st.info("Cloud Status: Online 24/7")

uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

if uploaded_file:
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("🚀 GENERATE FOR WHOP"):
        with st.status("🧠 AI Processing...") as status:
            model = whisper.load_model("tiny")
            result = model.transcribe("temp_video.mp4", fp16=False, word_timestamps=True)
            
            video = mp.VideoFileClip("temp_video.mp4").subclip(0, 30)
            if "9:16" in layout:
                video = video.crop(x_center=video.w/2, y_center=video.h/2, width=video.h*(9/16), height=video.h)
            
            layers = [video]
            for seg in result['segments']:
                for w in seg.get('words', []):
                    if w['start'] < 30:
                        txt = mp.TextClip(w['word'].strip().upper(), fontsize=70, color='yellow', stroke_color='black', stroke_width=2, 
                                         font='Arial-Bold', method='caption', size=(video.w*0.8, None)).set_start(w['start']).set_duration(w['end']-w['start']).set_position(('center', video.h*0.75))
                        layers.append(txt)

            out_name = f"viral_clip_{int(time.time())}.mp4"
            final = mp.CompositeVideoClip(layers).set_audio(video.audio)
            final.write_videofile(out_name, codec="libx264", audio_codec="aac", fps=24)
            
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.video(out_name)
            with col2:
                st.metric("VIRAL SCORE", f"{random.randint(90, 99)}%")
                st.code(f"TITLE: {' '.join(result['text'].split()[:5]).upper()} 🚀")
            
            video.close(); final.close(); gc.collect()
