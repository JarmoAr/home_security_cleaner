import os
import shutil
import streamlit as st
from pathlib import Path
import cv2

# Import custom services
import sample_service
import analyze_results
from config import ARCHIVE_PATH, AI_RESULTS_PATH, DELETE_PATH

# 1. Page Configuration
st.set_page_config(page_title="Security AI Control Center", page_icon="🛡️", layout="wide")

# ==============================================================================
# 🔑 SECURE LOCAL PASSWORD PROTECTION SYSTEM
# ==============================================================================
def check_password():
    """Verifies user credentials securely against secrets.toml."""
    def password_entered():
        if (st.session_state["username"] == st.secrets["DASHBOARD_USERNAME"] and 
            st.session_state["password"] == st.secrets["DASHBOARD_PASSWORD"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
            st.rerun()
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Security AI Dashboard - Login Required")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Log In", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Security AI Dashboard - Login Required")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Log In", on_click=password_entered)
        st.error("❌ Invalid Username or Password. Please try again.")
        return False
    else:
        return True

if not check_password():
    st.stop()
# ==============================================================================

st.title("🛡️ Security Camera AI - Control Center")
st.subheader("Manage alerts, train algorithms, and audit the 30-day trash quarantine")

# Resolve core paths from config architecture
archive_dir = str(ARCHIVE_PATH)
ai_results_dir = str(AI_RESULTS_PATH)
trash_dir = str(DELETE_PATH)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Sidebar configuration navigation options
st.sidebar.header("📁 Navigation & Queues")
view_mode = st.sidebar.radio("Go to section:", ["Review Alerts (Archive)", "Audit Trash (Quarantine)", "View AI Model Templates"])

# ==============================================================================
# SECTION 1: REVIEW ALERTS (ARCHIVE) - CHRONOLOGICAL REVERSE SORT
# ==============================================================================
if view_mode == "Review Alerts (Archive)":
    if os.path.exists(archive_dir):
        # Fetch files and sort them dynamically by modification time (Newest First)
        raw_videos = [f for f in os.listdir(archive_dir) if f.endswith(('.mp4', '.avi', '.mkv'))]
        videos = sorted(raw_videos, key=lambda x: os.path.getmtime(os.path.join(archive_dir, x)), reverse=True)
    else:
        videos = []
    
    if not videos:
        st.info("🎉 The archive directory is clean! No mystery videos to review right now.")
    else:
        selected_video_name = st.sidebar.selectbox("Select an archived video (Newest first):", videos)
        full_video_path = os.path.join(archive_dir, selected_video_name)
        
        col1, col2 = st.columns([1.2, 1.0])
        with col1:
            st.markdown(f"### 📹 Video Playback: `{selected_video_name}`")
            st.video(full_video_path)
            
            st.markdown("---")
            st.markdown("### 🔍 Visual AI Debugger (`ai_results`)")
            if st.button("🚀 Run Visual AI Debugger on this Video", use_container_width=True, type="primary"):
                with st.spinner("Creating copy for AI Results and rendering target frames..."):
                    try:
                        os.makedirs(ai_results_dir, exist_ok=True)
                        target_debug_path = os.path.join(ai_results_dir, selected_video_name)
                        shutil.copy(full_video_path, target_debug_path)
                        
                        analyze_results.analyze_video_individually(target_debug_path, ai_results_dir)
                        st.success("Analysis complete! Bounding box images generated below.")
                        
                        generated_images = [f for f in os.listdir(ai_results_dir) if f.startswith(os.path.splitext(selected_video_name)) and f.endswith(('.jpg', '.jpeg', '.png'))]
                        if generated_images:
                            for img_name in sorted(generated_images):
                                st.image(os.path.join(ai_results_dir, img_name), caption=img_name, use_container_width=True)
                        else:
                            st.warning("YOLOv8 did not find any distinct targets to draw on this video.")
                    except Exception as e:
                        st.error(f"Error during debugger run: {e}")
            
        with col2:
            st.markdown("### 🧠 AI Retraining Actions")
            if st.button("🛞 Extract as 'Own Vehicle' (car)", use_container_width=True):
                success = sample_service.extract_new_sample(full_video_path, "car", "images/auto", "own_car")
                st.success("✅ Vehicle template extracted!") if success else st.error("No clear vehicle found.")
                        
            if st.button("👤 Extract as 'Known Person' (person)", use_container_width=True):
                success = sample_service.extract_new_sample(full_video_path, "person", "images/ihmiset", "known_person")
                st.success("✅ Human facial template extracted!") if success else st.error("No clear face found.")
                        
            if st.button("🐾 Extract as 'Own Dog' (dog)", use_container_width=True):
                success = sample_service.extract_new_sample(full_video_path, "dog", "images/koira", "own_dog")
                st.success("✅ Dog template extracted!") if success else st.error("No clear dog found.")

            st.markdown("### 🔒 Final Action")
            if st.button("🗑️ Done with Video (Move to Trash)", use_container_width=True, type="secondary"):
                try:
                    shutil.move(full_video_path, os.path.join(trash_dir, selected_video_name))
                    if os.path.exists(ai_results_dir):
                        for f in os.listdir(ai_results_dir):
                            os.remove(os.path.join(ai_results_dir, f)) if os.path.isfile(os.path.join(ai_results_dir, f)) else None
                    st.warning("Video moved to trash and debugger cache completely wiped!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to move file: {e}")

# ==============================================================================
# SECTION 2: AUDIT TRASH - CHRONOLOGICAL REVERSE SORT
# ==============================================================================
elif view_mode == "Audit Trash (Quarantine)":
    st.markdown("### 🗑️ Trash Quarantine Vault (30-day Rolling Buffer)")
    st.write("These videos were classified as safe (e.g., Own Car) and sent to trash. Review them below to ensure no false negatives occurred.")
    
    if os.path.exists(trash_dir):
        # Fetch files and sort them dynamically by modification time (Newest First)
        raw_trash = [f for f in os.listdir(trash_dir) if f.endswith(('.mp4', '.avi', '.mkv'))]
        trash_videos = sorted(raw_trash, key=lambda x: os.path.getmtime(os.path.join(trash_dir, x)), reverse=True)
    else:
        trash_videos = []
    
    if not trash_videos:
        st.info("Empty! There are no videos currently waiting inside the trash quarantine buffer.")
    else:
        selected_trash_name = st.sidebar.selectbox("Select a trashed video (Newest first):", trash_videos)
        full_trash_path = os.path.join(trash_dir, selected_trash_name)
        
        col1, col2 = st.columns([1.2, 1.0])
        with col1:
            st.markdown(f"### 📹 Video Playback: `{selected_trash_name}`")
            st.video(full_trash_path)
            
        with col2:
            st.markdown("### 🔄 Quarantine Rescue")
            st.write("If the AI made a mistake and this video contains something important, restore it instantly back to the active archive queue:")
            
            if st.button("🚀 Restore Video back to Archive List", use_container_width=True, type="primary"):
                try:
                    shutil.move(full_trash_path, os.path.join(archive_dir, selected_trash_name))
                    st.toast(f"✅ Restored {selected_trash_name} back to Archive Alerts!")
                    st.rerun()
                except Exception as restore_err:
                    st.error(f"Failed to restore file from quarantine: {restore_err}")

# ==============================================================================
# SECTION 3: VIEW AI MODEL TEMPLATES
# ==============================================================================
elif view_mode == "View AI Model Templates":
    st.markdown("### 🖼️ Active AI Model Templates")
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
