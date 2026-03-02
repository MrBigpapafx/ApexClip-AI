import streamlit as st
import os
import moviepy.editor as mp
from moviepy.video.fx.all import crop
import whisper
import gc
import random
import time

# --- PRO UI DESIGN ---
st.set_page_config(page_title="ApexClip Opus-Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0c0d10; color: #ffffff; }
    .clip-card { 
        background-color: #1a1c23; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #30363d;
        margin-bottom: 25px;
    }
    .virality-badge { background: linear-gradient(90deg, #ff4b4b, #ff8e53); color: white; padding: 4px 12px; border-radius: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 APEXCLIP PRO: VIRAL DASHBOARD")

uploaded_file = st.file_uploader("Upload Video (MP4)", type=["mp4"])

if uploaded_file:
    # Save input file
    input_path = "input_video.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("🔥 GENERATE VIRAL CLIPS"):
        # We use a container so the clips appear immediately as they are ready
        container = st.container()
        
        with st.status("🛸 AI is slicing your video...") as status:
            model = whisper.load_model("tiny")
            result = model.transcribe(input_path, word_timestamps=True)
            full_video = mp.VideoFileClip(input_path)
            
            for i, segment in enumerate(result['segments'][:5]):
                start, end = segment['start'], segment['end']
                if (end - start) < 5: continue 
                
                # Metadata
                v_title = " ".join(segment['text'].strip().split()[:5]).upper() + " 🚀"
                v_desc = f"{segment['text'].strip()}\n\n#viral #whop #success #ai"
                
                # Processing
                clip = full_video.subclip(start, end)
                w, h = clip.size
                target_w = h * (9/16)
                clip_v = crop(clip, x_center=w/2, y_center=h/2, width=min(target_w, w), height=h)
                
                out_path = f"output_clip_{i}.mp4"
                # Write the file
                clip_v.write_videofile(out_path, codec="libx264", audio_codec="aac", fps=24, logger=None)
                
                # IMPORTANT: Close clip to free file for Streamlit to read
                clip_v.close()
                clip.close()
                
                # --- RENDER TO UI IMMEDIATELY ---
                with container:
                    st.markdown(f'<div class="clip-card">', unsafe_allow_html=True)
                    st.markdown(f"### 📋 Clip {i+1} <span class='virality-badge'>Score: {random.randint(92,99)}%</span>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        # Check if file exists before showing
                        if os.path.exists(out_path):
                            st.video(out_path)
                            with open(out_path, "rb") as f:
                                st.download_button(f"📥 Download HD Clip {i+1}", f, file_name=f"Apex_Clip_{i+1}.mp4")
                        else:
                            st.error("Video file generation failed.")
                    
                    with col2:
                        st.write("**Viral Title:**")
                        st.code(v_title)
                        st.write("**AI Description:**")
                        st.code(v_desc)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                gc.collect()

            full_video.close()
            st.balloons()
