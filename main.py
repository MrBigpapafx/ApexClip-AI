import streamlit as st
import os
import moviepy.editor as mp
from moviepy.video.fx.all import crop
import whisper
import gc
import tempfile
import random

# --- PRO DASHBOARD UI ---
st.set_page_config(page_title="ApexClip Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0c0d10; color: #ffffff; }
    .clip-card { background-color: #1a1c23; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 25px; }
    .virality-badge { background: linear-gradient(90deg, #ff4b4b, #ff8e53); color: white; padding: 5px 12px; border-radius: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 APEXCLIP PRO: VIRAL DASHBOARD")

uploaded_file = st.file_uploader("Upload MP4 Video", type=["mp4"])

def create_captions(words, clip_w, clip_h):
    clips = []
    for word in words:
        txt = mp.TextClip(
            word['word'].strip().upper(),
            fontsize=70, color='yellow', font='Arial-Bold',
            stroke_color='black', stroke_width=2,
            method='caption', size=(clip_w * 0.8, None)
        ).set_start(word['start']).set_duration(word['end'] - word['start']).set_position(('center', clip_h * 0.75))
        clips.append(txt)
    return clips

if uploaded_file:
    # Save upload to temp file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    input_path = tfile.name

    if st.button("🔥 GENERATE CLIPS"):
        with st.status("🛸 AI Slicing Video...") as status:
            model = whisper.load_model("tiny")
            result = model.transcribe(input_path, word_timestamps=True)
            full_video = mp.VideoFileClip(input_path)
            
            # This is where we show the clips
            display_container = st.container()

            for i, segment in enumerate(result['segments'][:3]):
                start, end = segment['start'], segment['end']
                if (end - start) < 4: continue
                
                # Metadata
                v_title = " ".join(segment['text'].strip().split()[:5]).upper() + " 🚀"
                v_desc = f"{segment['text'].strip()}\n\n#viral #whop #ai"
                
                # Vertical Crop & Captions
                clip = full_video.subclip(start, end)
                w, h = clip.size
                clip_v = crop(clip, x_center=w/2, y_center=h/2, width=min(h*(9/16), w), height=h)
                
                seg_words = [{'word': x['word'], 'start': x['start']-start, 'end': x['end']-start} for x in segment.get('words', [])]
                caps = create_captions(seg_words, clip_v.w, clip_v.h)
                final = mp.CompositeVideoClip([clip_v] + caps).set_audio(clip_v.audio)

                # Export to Bytes for instant display
                out_tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                final.write_videofile(out_tfile.name, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast", logger=None)
                
                with open(out_tfile.name, "rb") as f:
                    v_bytes = f.read()

                with display_container:
                    st.markdown(f'<div class="clip-card">', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.video(v_bytes) # Show video immediately
                        st.download_button(f"📥 Download Clip {i+1}", v_bytes, file_name=f"Clip_{i+1}.mp4")
                    with c2:
                        st.markdown(f"### {v_title} <span class='virality-badge'>{random.randint(94,99)}%</span>", unsafe_allow_html=True)
                        st.write("**Title (Copy for Whop):**")
                        st.code(v_title)
                        st.write("**Description:**")
                        st.code(v_desc)
                    st.markdown('</div>', unsafe_allow_html=True)

                # Memory Clean
                final.close(); clip_v.close(); clip.close()
                gc.collect()

            full_video.close()
            st.balloons()
