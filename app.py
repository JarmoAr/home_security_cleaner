import os
import streamlit as st
from pathlib import Path
import vision_service
import sample_service
from config import ARCHIVE_PATH

# 1. Page Configuration
st.set_page_config(page_title="Security AI Training Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Security Camera AI - Training & Review Dashboard")
st.subheader("Correct AI mistakes by extracting new training templates from archived videos")

# 2. Resolve Paths
archive_dir = str(ARCHIVE_PATH)

# 3. Fetch archived videos
if os.path.exists(archive_dir):
    videos = [f for f in os.listdir(archive_dir) if f.endswith(('.mp4', '.avi', '.mkv'))]
else:
    videos = []

if not videos:
    st.info("🎉 The archive directory is clean! No mystery videos to review right now.")
else:
    # Sidebar selection for the videos
    st.sidebar.header("📁 Archived Videos")
    selected_video_name = st.sidebar.selectbox("Select a video to retrain AI:", videos)
    
    full_video_path = os.path.join(archive_dir, selected_video_name)
    
    # Create layout columns: Left for Video, Right for AI Actions
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 📹 Reviewing: `{selected_video_name}`")
        # Streamlit renders the video natively for web playback
        st.video(full_video_path)
        
    with col2:
        st.markdown("### 🧠 AI Retraining Actions")
        st.write("If the AI failed to recognize a known target in this video, extract a new visual template below to update the model databank:")
        
        st.divider()
        
        # Action 1: Train Vehicle
        if st.button("🛞 Extract as 'Own Vehicle' (car)", use_container_width=True):
            with st.spinner("Processing video frames for vehicle extraction..."):
                success = sample_service.extract_new_sample(full_video_path, "car", "images/auto", "own_car")
                if success:
                    st.success("Successfully updated Vehicle templates!")
                else:
                    st.error("Could not find a clear vehicle in this video.")
                    
        st.divider()

        # Action 2: Train Family Member
        if st.button("👤 Extract as 'Known Person' (person)", use_container_width=True):
            with st.spinner("Scanning frames for clear facial profile..."):
                success = sample_service.extract_new_sample(full_video_path, "person", "images/ihmiset", "known_person")
                if success:
                    st.success("Successfully updated Known Person facial templates!")
                else:
                    st.error("Could not find a clear person with a visible face in this video.")
                    
        st.divider()

        # Action 3: Train Dog
        if st.button("🐾 Extract as 'Own Dog' (dog)", use_container_width=True):
            with st.spinner("Extracting dog coat and color histograms..."):
                success = sample_service.extract_new_sample(full_video_path, "dog", "images/koira", "own_dog")
                if success:
                    st.success("Successfully updated Dog templates!")
                else:
                    st.error("Could not find a clear dog in this video.")

        st.divider()
        
        # Safe dismissal: Move out of archive if it was just a false alarm
        if st.button("🗑️ Dismiss Video (Move to Trash)", use_container_width=True, type="secondary"):
            import shutil
            from config import DELETE_PATH
            trash_path = os.path.join(str(DELETE_PATH), selected_video_name)
            try:
                shutil.move(full_video_path, trash_path)
                st.warning(f"Video moved to trash. Refreshing...")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to move file: {e}")
