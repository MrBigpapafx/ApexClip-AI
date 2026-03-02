import streamlit as st
import os
import moviepy.editor as mp
from moviepy.video.fx.all import crop
import whisper
import gc
import random

# --- PRO UI DESIGN ---
st.set_page_config(page_title="ApexClip Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #0c0d10; color: #fff; } .clip-card { background: #1a1c23; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #333; }</style>", unsafe_allow_html=True)

st.title("🚀 APEXCLIP PRO: VIRAL DASHBOARD")

uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

if uploaded_file:
    # 1. Save input to a solid path
    input_path = os.path.join(os.getcwd(), "input_video.mp4")
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("🔥 GENERATE VIRAL CLIPS"):
        with st.status("🛸 AI is scanning and rendering...") as status:
            # Load AI
            model = whisper.load_model("tiny")
            result = model.transcribe(input_path)
            full_video = mp.VideoFileClip(input_path)
            
            # We will store clip info here to show them later
            generated_clips = []

            for i, segment in enumerate(result['segments'][:3]): # Start with 3 to test speed
                start, end = segment['start'], segment['end']
                if (end - start) < 4: continue
                
                # Metadata
                v_title = " ".join(segment['text'].strip().split()[:5]).upper() + " 🚀"
                v_desc = f"{segment['text'].strip()}\n\n#viral #whop #ai"
                
                # Vertical Crop Logic
                clip = full_video.subclip(start, end)
                w, h = clip.size
                target_w = h * (9/16)
                clip_v = crop(clip, x_center=w/2, y_center=h/2, width=min(target_w, w), height=h)
                
                # SAVE PROCESS - Essential for Cloud
                out_name = f"clip_{i}.mp4"
                out_path = os.path.join(os.getcwd(), out_name)
                
                # Using 'libx264' is the secret for web playback
                clip_v.write_videofile(out_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, fps=24, logger=None)
                
                # Store data
                generated_clips.append({"path": out_path, "title": v_title, "desc": v_desc, "name": out_name})
                
                clip_v.close()
                clip.close()
                gc.collect()

            full_video.close()

        # --- DISPLAY RESULTS ---
        for clip_data in generated_clips:
            with st.container():
                st.markdown(f'<div class="clip-card">', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if os.path.exists(clip_data["path"]):
                        # Open as binary so Streamlit doesn't lose the path
                        with open(clip_data["path"], "rb") as v_file:
                            st.video(v_file.read())
                            st.download_button(f"📥 Download {clip_data['name']}", v_file, file_name=clip_data['name'])
                
                with col2:
                    st.subheader(clip_data["title"])
                    st.code(clip_data["desc"])
                st.markdown('</div>', unsafe_allow_html=True)
