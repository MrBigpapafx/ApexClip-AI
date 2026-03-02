import streamlit as st
import os
import moviepy.editor as mp
from moviepy.video.fx.all import crop
import whisper
import gc
import tempfile

# --- PRO UI DESIGN ---
st.set_page_config(page_title="ApexClip Opus-Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #0c0d10; color: #fff; } .clip-card { background: #1a1c23; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 30px; }</style>", unsafe_allow_html=True)

st.title("🚀 APEXCLIP PRO: VIRAL DASHBOARD")

uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

def create_captions(words, clip_w, clip_h):
    """Memory-efficient word-by-word captions"""
    caption_clips = []
    for word in words:
        txt = mp.TextClip(
            word['word'].strip().upper(),
            fontsize=65, color='yellow', font='Arial-Bold',
            stroke_color='black', stroke_width=2,
            method='caption', size=(clip_w * 0.8, None)
        ).set_start(word['start']).set_duration(word['end'] - word['start']).set_position(('center', clip_h * 0.75))
        caption_clips.append(txt)
    return caption_clips

if uploaded_file:
    # Use TempFile to avoid 'File in use' errors
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(uploaded_file.read())
        input_path = tmp.name

    if st.button("🔥 GENERATE VIRAL CLIPS"):
        with st.status("🧠 AI Scanning Hooks...") as status:
            # Load AI (Tiny model saves 400MB of RAM)
            model = whisper.load_model("tiny")
            result = model.transcribe(input_path, word_timestamps=True)
            full_video = mp.VideoFileClip(input_path)
            
            # Dashboard container
            results_area = st.container()

            for i, segment in enumerate(result['segments'][:3]):
                start, end = segment['start'], segment['end']
                if (end - start) < 4: continue
                
                # Metadata
                v_title = " ".join(segment['text'].strip().split()[:5]).upper() + " 🚀"
                v_desc = f"{segment['text'].strip()}\n\n#viral #whop #ai"
                
                # 1. Vertical Crop
                clip = full_video.subclip(start, end)
                w, h = clip.size
                target_w = h * (9/16)
                clip_v = crop(clip, x_center=w/2, y_center=h/2, width=min(target_w, w), height=h)
                
                # 2. Add Word Captions
                seg_words = []
                for w_obj in segment.get('words', []):
                    seg_words.append({'word': w_obj['word'], 'start': w_obj['start'] - start, 'end': w_obj['end'] - start})
                
                caps = create_captions(seg_words, clip_v.w, clip_v.h)
                final_clip = mp.CompositeVideoClip([clip_v] + caps).set_audio(clip_v.audio)

                # 3. Export with 'Ultra-Fast' preset to save CPU/Memory
                out_path = f"clip_{i}.mp4"
                final_clip.write_videofile(
                    out_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    fps=24, 
                    preset="ultrafast", # Crucial for Streamlit Cloud
                    logger=None,
                    threads=1 # Single thread prevents memory spikes
                )
                
                # 4. Stream to UI
                with open(out_path, "rb") as f:
                    v_bytes = f.read()

                with results_area:
                    st.markdown('<div class="clip-card">', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.video(v_bytes)
                        st.download_button(f"📥 Download Clip {i+1}", v_bytes, file_name=f"Clip_{i+1}.mp4")
                    with c2:
                        st.subheader(v_title)
                        st.code(v_desc)
                    st.markdown('</div>', unsafe_allow_html=True)

                # 5. HARD CLEANUP
                final_clip.close(); clip_v.close(); clip.close()
                del final_clip, clip_v, clip, v_bytes
                gc.collect()

            full_video.close()
            st.balloons()
