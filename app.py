import os
import shutil
import streamlit as st
from pathlib import Path
import cv2

# Import custom services
import sample_service
import analyze_results
from config import ARCHIVE_PATH, AI_RESULTS_PATH

# 1. Page Configuration
st.set_page_config(page_title="Security AI Control Center", page_icon="🛡️", layout="wide")

st.title("🛡️ Security Camera AI - Control Center")
st.subheader("Review alerts, run visual debuggers, and manage training templates")

# Resolve core paths
archive_dir = str(ARCHIVE_PATH)
ai_results_dir = str(AI_RESULTS_PATH)
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Fetch Archived Videos
if os.path.exists(archive_dir):
    videos = [f for f in os.listdir(archive_dir) if f.endswith(('.mp4', '.avi', '.mkv'))]
else:
    videos = []

# Sidebar configuration
st.sidebar.header("📁 Navigation & Videos")
view_mode = st.sidebar.radio("Go to section:", ["Review & Retrain AI", "View AI Model Templates"])

# ==============================================================================
# SECTION 1: REVIEW & RETRAIN AI (WITH VISUAL DEBUGGER)
# ==============================================================================
if view_mode == "Review & Retrain AI":
    if not videos:
        st.info("🎉 The archive directory is clean! No mystery videos to review right now.")
    else:
        selected_video_name = st.sidebar.selectbox("Select an archived video:", videos)
        full_video_path = os.path.join(archive_dir, selected_video_name)
        
        # UI Columns: Left for Video, Right for Controls
        col1, col2 = st.columns([1.2, 1.0])
        
        with col1:
            st.markdown(f"### 📹 Video Playback: `{selected_video_name}`")
            st.video(full_video_path)
            
            # --- VISUAL AI DEBUGGER SECTION ---
            st.markdown("---")
            st.markdown("### 🔍 Visual AI Debugger (`ai_results`)")
            st.write("Run the offline analysis tool to extract and draw bounding boxes on detected objects.")
            
            if st.button("🚀 Run Visual AI Debugger on this Video", use_container_width=True, type="primary"):
                with st.spinner("Moving video to AI Results and rendering target frames..."):
                    try:
                        # Ensure target directory exists
                        os.makedirs(ai_results_dir, exist_ok=True)
                        target_debug_path = os.path.join(ai_results_dir, selected_video_name)
                        
                        # Move the file from archive to ai_results so analyze_results.py can see it
                        shutil.move(full_video_path, target_debug_path)
                        
                        # Run the analyzer module that bakes bounding boxes onto images
                        analyze_results.analyze_video_individually(target_debug_path, ai_results_dir)
                        st.success("Analysis complete! Bounding box images generated inside `ai_results` directory.")
                        
                        # Instantly fetch and display the generated .jpg images on the webpage
                        generated_images = [f for f in os.listdir(ai_results_dir) if f.startswith(os.path.splitext(selected_video_name)[0]) and f.endswith(('.jpg', '.jpeg', '.png'))]
                        
                        if generated_images:
                            st.markdown("#### 🖼️ AI Detection Screenshots:")
                            for img_name in sorted(generated_images):
                                img_path = os.path.join(ai_results_dir, img_name)
                                st.image(img_path, caption=f"AI Annotation: {img_name}", use_container_width=True)
                        else:
                            st.warning("YOLOv8 did not find any distinct targets to draw on this video.")
                            
                    except Exception as e:
                        st.error(f"Error during debugger run: {e}")
            
        with col2:
            st.markdown("### 🧠 AI Retraining Actions")
            st.write("Extract new templates from this video to teach the AI what is family-safe:")
            
            # Action 1: Train Vehicle
            if st.button("🛞 Extract as 'Own Vehicle' (car)", use_container_width=True):
                with st.spinner("Processing video frames for vehicle extraction..."):
                    if os.path.exists(full_video_path):
                        success = sample_service.extract_new_sample(full_video_path, "car", "images/auto", "own_car")
                        st.success("Successfully updated vehicle templates!") if success else st.error("No clear vehicle found.")
                    else:
                        st.error("Video file was moved by the debugger. Refresh the page.")
                        
            st.divider()

            # Action 2: Train Family Member
            if st.button("👤 Extract as 'Known Person' (person)", use_container_width=True):
                with st.spinner("Scanning frames for clear facial profile..."):
                    if os.path.exists(full_video_path):
                        success = sample_service.extract_new_sample(full_video_path, "person", "images/ihmiset", "known_person")
                        st.success("Successfully updated human facial templates!") if success else st.error("No clear face found.")
                    else:
                        st.error("Video file was moved by the debugger. Refresh the page.")
                        
            st.divider()

            # Action 3: Train Dog
            if st.button("🐾 Extract as 'Own Dog' (dog)", use_container_width=True):
                with st.spinner("Extracting dog coat and color histograms..."):
                    if os.path.exists(full_video_path):
                        success = sample_service.extract_new_sample(full_video_path, "dog", "images/koira", "own_dog")
                        st.success("Successfully updated dog templates!") if success else st.error("No clear dog found.")
                    else:
                        st.error("Video file was moved by the debugger. Refresh the page.")

            st.divider()
            
            # Action 4: Dismiss to Trash
            if st.button("🗑️ Dismiss Video (Move to Trash)", use_container_width=True, type="secondary"):
                from config import DELETE_PATH
                trash_target = os.path.join(str(DELETE_PATH), selected_video_name)
                try:
                    if os.path.exists(full_video_path):
                        shutil.move(full_video_path, trash_target)
                        st.warning("Moved to trash. Refreshing...")
                        st.rerun()
                    else:
                        st.error("Video was already moved by the debugger. Refresh the page.")
                except Exception as e:
                    st.error(f"Failed to move file: {e}")

# ==============================================================================
# SECTION 2: VIEW AI MODEL TEMPLATES (YOUR REFERENCE IMAGES)
# ==============================================================================
elif view_mode == "View AI Model Templates":
    st.markdown("### 🖼️ Active AI Model Templates")
    st.write("These are your authorized reference images. The AI uses these files to determine what belongs to your house vs. what is a stranger.")
    
    categories = {
        "🛞 Authorized Vehicles (images/auto)": os.path.join(script_dir, "images", "auto"),
        "👤 Known Residents (images/ihmiset)": os.path.join(script_dir, "images", "ihmiset"),
        "🐾 Family Pets / Dog (images/koira)": os.path.join(script_dir, "images", "koira")
    }
    
    for cat_title, cat_path in categories.items():
        st.markdown(f"#### {cat_title}")
        if os.path.exists(cat_path):
            template_files = [f for f in os.listdir(cat_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
            
            if template_files:
                # Display templates in a grid layout (4 images per row)
                cols = st.columns(4)
                for index, file_name in enumerate(template_files):
                    col_target = cols[index % 4]
                    full_img_path = os.path.join(cat_path, file_name)
                    with col_target:
                        st.image(full_img_path, caption=file_name, use_container_width=True)
            else:
                st.info(f"No reference images found in `{cat_path}` yet. Use the training buttons to add samples!")
        else:
            st.error(f"Template folder missing on server disk: `{cat_path}`")
