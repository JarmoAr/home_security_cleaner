# 🛡️ Smart Security Camera System & Real-Time AI Watcher

This application automates the management, AI analysis, and cleanup of security camera video files. The system continuously watches a local directory for incoming camera feeds, analyzes them in real-time using computer vision (YOLOv8, Color Histograms, and Face Recognition), and automatically filters out videos containing only known residents, vehicles, or family pets.

---

## 📋 1. Purpose and Logic
*   **Real-Time Directory Watching:** The system continuously monitors an incoming directory for new `.mp4` video files. Once a file is stable (camera finishes writing), it is instantly processed.
*   **Dynamic File Routing:** Videos pass through a secure local processing pipeline: `incoming_videos` -> `temp` -> `archive` (if a threat is detected) or `trash` (local trash bin with a 30-day retention policy).
*   **Multilayered AI Filtering:** Detected objects are intelligently cross-referenced against local templates. Only unrecognized or suspicious entities trigger a critical alert and permanent archiving.
*   **Power Outage Recovery:** Upon system startup, the system automatically checks the watch directory and processes any backlogged files sequentially from oldest to newest.

---

## 🏗️ 2. System Architecture

### Directories and Locations (User Home / BASE_DIR)
*   `~/security_camera/incoming_videos/` - The active directory where the security camera deposits new `.mp4` files.
*   `~/security_camera/temp/` - A secure temporary directory where files are moved for isolated AI analysis.
*   `~/security_camera/archive/` - Permanent storage for verified alerts (unrecognized persons or vehicles).
*   `~/security_camera/trash/` - Local trash bin for safe videos (automatically deleted after 30 days).
*   `~/security_camera/samples/` - A dedicated directory for manual or semi-automatic template training.
*   `~/security_camera/ai_results/` - Target folder for the manual analysis utility.

### AI Template Databank (Project Repository)
*   `./images/auto/` - Reference images of authorized vehicles for dynamic 2D HSV color histogram matching.
*   `./images/ihmiset/` - Clear facial profile photos of residents for `face_recognition`.
*   `./images/koira/` - Color and coat templates of the family dog for flexible HSV matching thresholds.

### Python Modules
1.  `main.py`: The core application engine. Runs a continuous polling loop, manages file stability checks, handles exceptions gracefully, and orchestrates the video processing pipeline.
2.  `vision_service.py`: Executes multilayered computer vision analysis: YOLOv8 object detection, normalized 2D HSV color histogram correlation, and dynamic infrared/night-mode detection based on grayscale saturation mean values.
3.  `save_service.py`: Manages file metadata and ensures safe writing by automatically appending counters (e.g., `video(1).mp4`) to prevent filename overwriting.
4.  `cleaner_service.py`: Performs automatic retention maintenance by permanently purging files older than 30 days from the local trash folder.
5.  `name_service.py`: Converts raw millisecond timestamps into standardized, readable filename stamps (`YYYYMMDD_HHMMSS`).
6.  `log_service.py`: Implements a centralized, automated daily logging framework using `TimedRotatingFileHandler`. It automatically rotates logs at midnight and maintains a clean rolling 7-day backup window.
7.  `config.py`: Centralizes system environment configurations, path resolutions using `pathlib.Path`, and handles automatic initialization of missing core directories at boot.
8.  `sample_service.py`: An interactive CLI training utility that scans videos for specific targets, crops them via bounding boxes, and automatically populates the template image databank.
9.  `analyze_results.py`: An independent manual analysis tool used to inspect mystery videos, draw colored tracking boxes (`cv2.rectangle`), and bake visual AI classification labels directly onto video frames.

---

## ⚙️ 3. Detailed Workflow

1.  **System Boot & Log Initialization:** The application verifies all core folders. The rolling logging service is spawned, and the local storage cleanup script sweeps away expired videos from the trash bin.
2.  **Live Directory Polling:** The system continuously monitors the watch folder. When a file is found, the system tracks its byte size over a 100ms delta to guarantee the camera has finished saving it.
3.  **Isolation & Processing Stage:** The target video is moved into the `temp` sandbox to isolate the disk I/O and prevent the watcher loop from stalling.
4.  **Multilayered AI Analysis:**
    *   **YOLOv8 Inference:** The network detects primary targets (`person`, `car`, `truck`, `dog`).
    *   **Day Mode Verification:** If colors are present, vehicles and pets are validated using normalized 2D color histograms. Persons are passed into the deep face-matching engine.
    *   **Night Mode (Infrared):** If the image saturation falls below `8.0` (indicating an active IR illuminator), the color logic is bypassed. Vehicles are automatically verified using a customized wagon aspect-ratio threshold (width/height ratio > 1.2).
5.  **Smart Routing Execution:** If an entity resolves as `"unknown_person"`, `"unknown_car"`, or `"unknown_animal"`, a critical alert triggers, and the file is locked in the permanent archive. Otherwise, the video is safely routed to the trash folder.

---

## 🛠️ 4. Technical Specifications
*   **Core Libraries:** `ultralytics` (YOLOv8), `opencv-python` (OpenCV), `face_recognition`, `numpy`, `pytest`, `shutil`.
*   **Environment Compatibility:** Cross-platform layout built using Python's `pathlib`. Developed locally in Windows environments and natively supported in headless Linux cloud architectures.

---

## 🧪 5. Automated Quality Assurance (CI/CD)

The project relies on a native **Pytest** architecture for microservice integration testing and regression tracking, deprecating legacy end-to-end framework layers.

1.  **Continuous Integration:** GitHub Actions automatically intercepts every code push via `.github/workflows/tests.yml`.
2.  **Isolated Virtual Runs:** Cloud workflows spin up isolated Python execution runners, install exact library frames from `requirements.txt`, and fire the testing suite.
3.  **Mock Environment Security:** Unit test scenarios use Pytest's native `tmp_path` fixtures to construct temporary system directories, ensuring zero interference with real production camera logs or disk directories.

### Active Unit Test Coverage (`test_helpers.py`):
*   `test_format_timestamp_success`: Validates millisecond transformations to standard filename formats.
*   `test_format_timestamp_invalid`: Ensures mathematical and input errors are isolated gracefully without crashing.
*   `test_check_filename_no_duplicate`: Confirms pristine filenames are retained when target files do not clash.
*   `test_check_filename_with_duplicate`: Verifies auto-increment counters trigger correctly when duplicate files exist.

---
*Document updated: July 18, 2026 - Deprecated Gmail eräajot / Base64 parsing. Documented continuous directory watcher, Pytest CI infrastructure, automated midnight log rotation, and full English refactor.*
