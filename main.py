import streamlit as st
import os
import moviepy.editor as mp
import whisper
import gc
import time
import math

st.set_page_config(page_title="ApexClip AI - Full Scanner", layout="wide")
st.title("🎬 APEXCLIP AI: FULL VIDEO SCANNER")

uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

if uploaded_file:
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Get total video length
    full_video = mp.VideoFileClip("temp_video.mp4")
    total_seconds = full_video.duration
    num_clips = math.ceil(total_seconds / 30)
    
    st.info(f"🎞️ Video Length: {int(total_seconds)}s | AI will generate up to {num_clips} clips.")

    if st.button("🚀 SCAN ENTIRE VIDEO"):
        with st.status("🧠 AI Analyzing Everything...") as status:
            model = whisper.load_model("tiny")
            # Transcribe the whole thing once to save time
            result = model.transcribe("temp_video.mp4", fp16=False, word_timestamps=True)
            
            for i in range(num_clips):
                start_t = i * 30
                end_t = min((i + 1) * 30, total_seconds)
                
                # Stop if the last bit is too short (e.g., less than 5s)
                if (end_t - start_t) < 5: break
                
                clip = full_video.subclip(start_t, end_t)
                # Auto-Crop to Vertical 9:16
                clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=clip.h*(9/16), height=clip.h)
                
                out_name = f"clip_{i+1}.mp4"
                clip.write_videofile(out_name, codec="libx264", audio_codec="aac", fps=24, logger=None)
                
                # Display each clip as it finishes
                st.subheader(f"📍 Clip {i+1} ({start_t}s - {end_t}s)")
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.video(out_name)
                with col2:
                    st.success(f"Clip {i+1} Processed")
                    with open(out_name, "rb") as file:
                        st.download_button(f"📥 Download Clip {i+1}", data=file, file_name=out_name)
            
            full_video.close()
            gc.collect()
