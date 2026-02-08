import streamlit as st
from google import genai
from google.genai import types
import time

# Dashboard Configuration
st.set_page_config(page_title="Advance Business Consulting - VEO Studio", layout="wide")
st.title("🎬 VEO Video Studio (Pro)")

# Sidebar for Professional Controls
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d473530c84051d45c9859.svg", width=50)
    st.header("Control Panel")
    api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio or Vertex API key.")
    
    st.divider()
    model_choice = st.selectbox("Engine", ["veo-3.1-generate-preview", "veo-3.1-fast-generate-preview"])
    aspect_ratio = st.radio("Format", ["16:9 (Cinema)", "9:16 (Mobile/Social)"])
    resolution = st.selectbox("Resolution", ["1080p", "720p"])

# Main Interface
if not api_key:
    st.info("👋 Welcome. Please enter your API Key in the sidebar to activate the studio.")
else:
    client = genai.Client(api_key=api_key)

    # Maintain session for video chaining
    if "current_video_id" not in st.session_state:
        st.session_state.current_video_id = None

    prompt = st.text_area("Scene Description", height=150, placeholder="Example: A cinematic slow-motion shot of a bustling Karachi market at night, neon lights reflecting in rain puddles...")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Generate New 8s Clip", use_container_width=True):
            with st.spinner("Initializing AI Engine..."):
                operation = client.models.generate_videos(
                    model=model_choice,
                    prompt=prompt,
                    config=types.GenerateVideosConfig(aspect_ratio=aspect_ratio, resolution=resolution)
                )
                while not operation.done:
                    time.sleep(5)
                    operation = client.operations.get(operation)
                
                st.session_state.current_video_id = operation.response.generated_videos[0].video
                st.success("Generation Complete!")

    with col2:
        # This is the "Barrier Breaker" - Extending the video
        if st.session_state.current_video_id:
            if st.button("➕ Extend Clip (+7s)", use_container_width=True):
                with st.spinner("Analyzing last frames for continuity..."):
                    operation = client.models.generate_videos(
                        model=model_choice,
                        prompt=f"Continue the action: {prompt}",
                        video=st.session_state.current_video_id # Chaining logic
                    )
                    while not operation.done:
                        time.sleep(5)
                        operation = client.operations.get(operation)
                    
                    st.session_state.current_video_id = operation.response.generated_videos[0].video
                    st.success("Video Extended!")

    # Video Player
    if st.session_state.current_video_id:
        st.divider()
        st.subheader("Preview Player")
        # Generate temporary download link for the player
        video_path = "temp_output.mp4"
        client.files.download(file=st.session_state.current_video_id, path=video_path)
        st.video(video_path)
