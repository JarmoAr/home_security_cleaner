import os
import shutil
import streamlit as st
from pathlib import Path
import cv2

# Import custom services
import sample_service
import analyze_results
from config import ARCHIVE_PATH, AI_RESULTS_PATH

# ==============================================================================
# 🔑 SECURE LOCAL PASSWORD PROTECTION SYSTEM
# ==============================================================================
def check_password():
    """
    Verifies user credentials securely against secrets.toml. 
    Returns True if authentication succeeds.
    """
    def password_entered():
        """
        Callback function to validate credentials and force a page rerun upon success.
        """
        if (st.session_state["username"] == st.secrets["DASHBOARD_USERNAME"] and 
            st.session_state["password"] == st.secrets["DASHBOARD_PASSWORD"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Clean memory for security
            del st.session_state["username"]
            st.rerun()  # FORCE RE-RENDER: This ensures the login page disappears instantly!
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run: Draw clean login interface forms
        st.title("🔐 Security AI Dashboard - Login Required")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Log In", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Authentication failed: Re-render input elements with error banner
        st.title("🔐 Security AI Dashboard - Login Required")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Log In", on_click=password_entered)
        st.error("❌ Invalid Username or Password. Please try again.")
        return False
    else:
        # Authentication succeeded
        return True

# Enforce security baseline inspection before rendering any dashboard elements
if not check_password():
    st.stop()  

# ==============================================================================

# 1. Page Configuration
st.set_page_config(page_title="Security AI Control Center", page_icon="🛡️", layout="wide")

st.title("🛡️ Security Camera AI - Control Center")
st.subheader("Review alerts, run visual debuggers, and manage training templates without losing your video")

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
# SECTION 1: REVIEW & RETRAIN AI (WITH COPIED VIDEO LOCK)
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
            st.write("Run the offline analysis tool. This creates a COPY of the video so it stays in your archive list.")
            
            if st.button("🚀 Run Visual AI Debugger on this Video", use_container_width=True, type="primary"):
                with st.spinner("Creating copy for AI Results and rendering target frames..."):
                    try:
                        # Ensure target directory exists
                        os.makedirs(ai_results_dir, exist_ok=True)
                        target_debug_path = os.path.join(ai_results_dir, selected_video_name)
                        
                        # KORJAUS: Tehdään COPY eikä MOVE, jotta alkuperäinen video ei katoa mihinkään!
                        shutil.copy(full_video_path, target_debug_path)
                        
                        # Run the analyzer module that bakes bounding boxes onto images
                        analyze_results.analyze_video_individually(target_debug_path, ai_results_dir)
                        st.success("Analysis complete! Bounding box images generated below.")
                        
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
            st.write("Extract multiple samples from this video sequentially. The video will stay active until dismissed.")
            
            # Action 1: Train Vehicle
            if st.button("🛞 Extract as 'Own Vehicle' (car)", use_container_width=True):
                with st.spinner("Processing video frames for vehicle extraction..."):
                    if os.path.exists(full_video_path):
                        success = sample_service.extract_new_sample(full_video_path, "car", "images/auto", "own_car")
                        if success:
                            st.success("✅ Vehicle template extracted! You can still train other objects from this video.")
                        else:
                            st.error("Could not find a clear vehicle in this video.")
                    else:
                        st.error("Video file not found.")
                        
            st.divider()

            # Action 2: Train Family Member
            if st.button("👤 Extract as 'Known Person' (person)", use_container_width=True):
                with st.spinner("Scanning frames for clear facial profile..."):
                    if os.path.exists(full_video_path):
                        success = sample_service.extract_new_sample(full_video_path, "person", "images/ihmiset", "known_person")
                        if success:
                            st.success("✅ Human facial template extracted! You can still train other objects from this video.")
                        else:
                            st.error("Could not find a clear face. The script automatically scanned all frames but found no facing profiles.")
                    else:
                        st.error("Video file not found.")
                        
            st.divider()

            # Action 3: Train Dog
            if st.button("🐾 Extract as 'Own Dog' (dog)", use_container_width=True):
                with st.spinner("Extracting dog coat and color histograms..."):
                    if os.path.exists(full_video_path):
                        success = sample_service.extract_new_sample(full_video_path, "dog", "images/koira", "own_dog")
                        if success:
                            st.success("✅ Dog template extracted! You can still train other objects from this video.")
                        else:
                            st.error("Could not find a clear dog in this video.")
                    else:
                        st.error("Video file not found.")

            st.divider()
            st.markdown("### 🔒 Final Action")
            st.write("When you are completely done extracting all objects, click below to move the video out of the archive:")
            
            # Action 4: Dismiss to Trash (Purges the entire ai_results directory to save disk space)
            if st.button("🗑️ Done with Video (Move to Trash)", use_container_width=True, type="secondary"):
                from config import DELETE_PATH
                trash_target = os.path.join(str(DELETE_PATH), selected_video_name)
                try:
                    if os.path.exists(full_video_path):
                        # 1. Move the verified video file from archive to trash quarantine
                        shutil.move(full_video_path, trash_target)
                        
                        # 2. BULK CLEANUP: Permanently delete every single file inside the ai_results scratchpad
                        if os.path.exists(ai_results_dir):
                            for filename in os.listdir(ai_results_dir):
                                file_to_remove = os.path.join(ai_results_dir, filename)
                                if os.path.isfile(file_to_remove):
                                    os.remove(file_to_remove)
                        
                        st.warning("Video moved to trash and all visual AI debugger files completely purged. Refreshing queue...")
                        st.rerun()
                    else:
                        st.error("Video file no longer exists in archive.")
                except Exception as e:
                    st.error(f"Failed to move file and completely empty AI results: {e}")

# ==============================================================================
# SECTION 2: VIEW AI MODEL TEMPLATES
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
