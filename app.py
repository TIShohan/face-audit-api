"""
Face Detection API - Flask Backend
Converts the Jupyter notebook face detection logic into a web service
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
import requests
import cv2
import sys
try:
    import mediapipe as mp
except ImportError:
    print("\n" + "="*60)
    print("CRITICAL ERROR: MediaPipe library is missing!")
    print("="*60)
    print("This application REQUIRES both MediaPipe and OpenCV DNN to achieve")
    print("near 100% accuracy. Single model detection is not allowed.")
    print("\nPlease install Python 3.12 and run:")
    print("pip install -r requirements.txt")
    print("="*60 + "\n")
    sys.exit(1)

import numpy as np
import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import zipfile
import io
import threading
import time

app = Flask(__name__, static_folder='static')
# Security: Limit upload size to 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
CORS(app)

# ==========================================
# ============== CONFIGURATION =============
# ==========================================
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
NO_FACE_FOLDER = 'no_face_images'
MODEL_FOLDER = 'Model'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(NO_FACE_FOLDER, exist_ok=True)

from apscheduler.schedulers.background import BackgroundScheduler
import shutil
import time

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'jobs_data') # Parent folder for all dynamic data

UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
RESULTS_FOLDER = os.path.join(DATA_DIR, 'results')
NO_FACE_FOLDER = os.path.join(DATA_DIR, 'no_face_images')
MODEL_FOLDER = os.path.join(BASE_DIR, 'Model') # Model stays in root
MAX_FILE_AGE_HOURS = 24  # Files older than this will be deleted

# Create directories (and the parent DATA_DIR implicitly)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(NO_FACE_FOLDER, exist_ok=True)

# Processing configuration (DEFAULTS)
DEFAULT_DOWNLOAD_TIMEOUT = 20
DEFAULT_MEDIAPIPE_CONF_THRESH = 0.80
DEFAULT_DNN_CONF_THRESH = 0.70
DEFAULT_NUM_THREADS = 6
DEFAULT_BATCH_SIZE = 50

# Global job storage (in production, use Redis or database)
jobs = {}
jobs_lock = threading.Lock()

# ==========================================
# ========== AUTO-CLEANUP SYSTEM ===========
# ==========================================

def cleanup_old_files():
    """Delete files older than MAX_FILE_AGE_HOURS"""
    now = time.time()
    cutoff = now - (MAX_FILE_AGE_HOURS * 3600)
    
    print(f"[{datetime.now().isoformat()}] Running auto-cleanup...")
    
    deleted_count = 0
    
    # Folders to clean
    folders = [UPLOAD_FOLDER, RESULTS_FOLDER, NO_FACE_FOLDER]
    
    for folder in folders:
        if not os.path.exists(folder):
            continue
            
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                filepath = os.path.join(root, name)
                try:
                    if os.path.getmtime(filepath) < cutoff:
                        os.remove(filepath)
                        deleted_count += 1
                except Exception as e:
                    print(f"Error deleting file {filepath}: {e}")
            
            # Clean empty directories
            for name in dirs:
                dirpath = os.path.join(root, name)
                try:
                    # If directory empty (and not one of the main folders), delete it
                    if not os.listdir(dirpath) and dirpath not in folders:
                        os.rmdir(dirpath)
                except Exception as e:
                    print(f"Error removing dir {dirpath}: {e}")

    if deleted_count > 0:
        print(f"[{datetime.now().isoformat()}] Cleanup complete. Deleted {deleted_count} old files.")

# Initialize Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_old_files, trigger="interval", hours=1)
scheduler.start()

# Ensure scheduler shuts down when app exits
import atexit
atexit.register(lambda: scheduler.shutdown())

# ==========================================
# ========== INITIALIZE MODELS =============
# ==========================================
mp_face_detection = mp.solutions.face_detection

prototxt_path = os.path.join(MODEL_FOLDER, "deploy.prototxt.txt")
model_path = os.path.join(MODEL_FOLDER, "res10_300x300_ssd_iter_140000.caffemodel")
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

# ==========================================
# ========== FACE DETECTION LOGIC ==========
# ==========================================

def download_image(url, timeout=DEFAULT_DOWNLOAD_TIMEOUT):
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except:
        return None

def detect_with_dnn(image, threshold=DEFAULT_DNN_CONF_THRESH):
    """Detect face using OpenCV DNN"""
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    return np.max(detections[0, 0, :, 2]) > threshold

def process_row(row, job_id, config):
    """Process a single row for face detection"""
    img_url = row.get("Check-In Photo")
    id_val = row.get("id", row.name)
    
    # Extract config
    timeout = config.get('download_timeout', DEFAULT_DOWNLOAD_TIMEOUT)
    mp_thresh = config.get('mediapipe_thresh', DEFAULT_MEDIAPIPE_CONF_THRESH)
    dnn_thresh = config.get('dnn_thresh', DEFAULT_DNN_CONF_THRESH)
    save_images = config.get('save_images', True)

    if pd.isna(img_url) or str(img_url).strip() == "":
        return row.name, "Skipped (empty URL)", ""

    image = download_image(str(img_url), timeout)

    if image is None:
        return row.name, "DOWNLOAD_ERROR", "Image could not be downloaded"

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # MediaPipe detection (Primary)
    with mp_face_detection.FaceDetection(min_detection_confidence=mp_thresh) as face_detector:
        results = face_detector.process(image_rgb)
        face_found = results.detections is not None and len(results.detections) > 0

    # Fallback to DNN if MediaPipe fails
    if not face_found:
        face_found = detect_with_dnn(image, dnn_thresh)

    if face_found:
        return row.name, "GOOD", ""
    else:
        # Save NO FACE image only if requested
        if save_images:
            job_folder = os.path.join(NO_FACE_FOLDER, job_id)
            os.makedirs(job_folder, exist_ok=True)
            save_path = os.path.join(job_folder, f"{id_val}_NOFACE.jpg")
            cv2.imwrite(save_path, image)
            return row.name, "NO FACE", f"Saved: {save_path}"
        else:
            return row.name, "NO FACE", "Image not saved (Config)"

def process_csv_job(job_id, csv_path, original_filename, config):
    """Background job to process CSV file"""
    try:
        # Self-healing: Ensure results folder exists
        os.makedirs(RESULTS_FOLDER, exist_ok=True)
        
        with jobs_lock:
            jobs[job_id]['status'] = 'processing'
            jobs[job_id]['started_at'] = datetime.now().isoformat()
        
        # Load CSV
        df = pd.read_csv(csv_path)
        total_rows = len(df)
        
        # Initialize Face_Status column if not exists
        if 'Face_Status' not in df.columns:
            df['Face_Status'] = ''
        
        df["Face_Status"] = df["Face_Status"].astype(str).replace('nan', '', regex=False)
        
        # Identify rows to process
        rows_to_process = df[
            (df["Face_Status"].isna()) | 
            (df["Face_Status"].astype(str).str.strip() == '') | 
            (df["Face_Status"] == 'DOWNLOAD_ERROR')
        ]
        
        processing_indices = rows_to_process.index.tolist()
        processing_count = len(processing_indices)
        
        with jobs_lock:
            jobs[job_id]['total_rows'] = total_rows
            jobs[job_id]['rows_to_process'] = processing_count
            jobs[job_id]['processed'] = 0
        
        if processing_count == 0:
            with jobs_lock:
                jobs[job_id]['status'] = 'completed'
                jobs[job_id]['message'] = 'All rows already processed'
            return
        
        # Counters
        good_count = 0
        noface_count = 0
        download_err_count = 0
        
        # Process with threading
        num_threads = config.get('num_threads', DEFAULT_NUM_THREADS)
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_idx = {
                executor.submit(process_row, row, job_id, config): original_idx
                for original_idx, row in df.loc[processing_indices].iterrows()
            }
            
            for future in as_completed(future_to_idx):
                # CHECK CANCELLATION
                if jobs[job_id].get('status') == 'cancelled':
                    print(f"Job {job_id} cancelled by user. Terminating threads...")
                    executor.shutdown(wait=False, cancel_futures=True)
                    # Save partial results so far
                    result_path = os.path.join(RESULTS_FOLDER, f"{job_id}_results.csv")
                    df.to_csv(result_path, index=False)
                    return

                original_idx = future_to_idx[future]
                
                try:
                    processing_idx, status, log_msg = future.result()
                    df.at[original_idx, "Face_Status"] = status
                    
                    if status == "GOOD":
                        good_count += 1
                    elif status == "NO FACE":
                        noface_count += 1
                    elif status == "DOWNLOAD_ERROR":
                        download_err_count += 1
                    
                except Exception as e:
                    df.at[original_idx, "Face_Status"] = "SYSTEM_ERROR"
                
                # Update progress
                with jobs_lock:
                    jobs[job_id]['processed'] += 1
                    jobs[job_id]['good_count'] = good_count
                    jobs[job_id]['noface_count'] = noface_count
                    jobs[job_id]['download_error_count'] = download_err_count
                
                # Save partial results every BATCH_SIZE rows
                # We use a temp lock or just overwrite, pandas atomic write is safest but simple overwrite works here
                # checking against BATCH_SIZE to reduce I/O
                if jobs[job_id]['processed'] % config.get('batch_size', DEFAULT_BATCH_SIZE) == 0:
                    result_path = os.path.join(RESULTS_FOLDER, f"{job_id}_results.csv")
                    df.to_csv(result_path, index=False)
        
        # Save FINAL results
        result_path = os.path.join(RESULTS_FOLDER, f"{job_id}_results.csv")
        df.to_csv(result_path, index=False)
        
        with jobs_lock:
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['result_file'] = result_path
            jobs[job_id]['completed_at'] = datetime.now().isoformat()
            jobs[job_id]['message'] = 'Processing completed successfully'
        
    except Exception as e:
        with jobs_lock:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = str(e)

# ==========================================
# ============== API ROUTES ================
# ==========================================

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    """Upload CSV file and start processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    # Get Config from Form Data
    try:
        config = {
            'download_timeout': int(request.form.get('download_timeout', DEFAULT_DOWNLOAD_TIMEOUT)),
            'mediapipe_thresh': float(request.form.get('mediapipe_thresh', DEFAULT_MEDIAPIPE_CONF_THRESH)),
            'dnn_thresh': float(request.form.get('dnn_thresh', DEFAULT_DNN_CONF_THRESH)),
            'num_threads': int(request.form.get('num_threads', DEFAULT_NUM_THREADS)),
            'batch_size': int(request.form.get('batch_size', DEFAULT_BATCH_SIZE)),
            'save_images': request.form.get('save_images', 'true').lower() == 'true'
        }
    except ValueError:
         return jsonify({'error': 'Invalid configuration values'}), 400

    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    filename = f"{job_id}_{file.filename}"
    
    # Ensure upload directory exists (Self-healing if deleted)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Initialize job
    with jobs_lock:
        jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'original_filename': file.filename,
            'uploaded_at': datetime.now().isoformat(),
            'config': config,
            'total_rows': 0,
            'rows_to_process': 0,
            'processed': 0,
            'good_count': 0,
            'noface_count': 0,
            'download_error_count': 0
        }
    
    # Start background processing
    thread = threading.Thread(target=process_csv_job, args=(job_id, filepath, file.filename, config))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'message': 'File uploaded successfully. Processing started.'
    }), 200

@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job processing status"""
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job_data = jobs[job_id].copy()
    
    # Calculate progress percentage
    if job_data.get('rows_to_process', 0) > 0:
        job_data['progress'] = (job_data['processed'] / job_data['rows_to_process']) * 100
    else:
        job_data['progress'] = 0
    
    return jsonify(job_data), 200

@app.route('/api/download/<job_id>', methods=['GET'])
def download_results(job_id):
    """Download processed CSV results"""
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = jobs[job_id]
        
        if job['status'] != 'completed':
            return jsonify({'error': 'Job not completed yet'}), 400
        
        result_file = job.get('result_file')
    
    if not result_file or not os.path.exists(result_file):
        return jsonify({'error': 'Result file not found'}), 404
    
    return send_file(
        result_file,
        as_attachment=True,
        download_name=f"processed_{job['original_filename']}"
    )

@app.route('/api/download-noface/<job_id>', methods=['GET'])
def download_noface_images(job_id):
    """Download NO FACE images as ZIP (Safe Temp File Method)"""
    job_folder = os.path.join(NO_FACE_FOLDER, job_id)
    
    if not os.path.exists(job_folder):
        return jsonify({'error': 'No images found'}), 404
    
    # Check if there are any files
    if not os.listdir(job_folder):
        return jsonify({'error': 'No images to zip'}), 404

    # Generate a secure temp filename
    zip_filename = f"{job_id}_noface"
    zip_path = os.path.join(RESULTS_FOLDER, zip_filename) # make_archive adds .zip extension automatically
    final_zip_path = zip_path + ".zip"

    try:
        # Create ZIP file on disk (Standard robust method)
        shutil.make_archive(zip_path, 'zip', job_folder)
        
        # Stream the file to the user
        def generate():
            with open(final_zip_path, 'rb') as f:
                while True:
                    chunk = f.read(4096 * 1024) # 4MB chunks
                    if not chunk:
                        break
                    yield chunk
            
            # Clean up after streaming is done
            try:
                os.remove(final_zip_path)
            except Exception as e:
                print(f"Error removing temp zip: {e}")

        response = app.response_class(
            generate(),
            mimetype='application/zip'
        )
        response.headers.set('Content-Disposition', 'attachment', filename=f'noface_images_{job_id}.zip')
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id):
    """Cancel a running job"""
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        # Mark as cancelled so the thread stops
        jobs[job_id]['status'] = 'cancelled'
        jobs[job_id]['message'] = 'Job cancelled by user'
        
    return jsonify({'message': 'Job cancellation requested'})

@app.route('/api/status/<job_id>', methods=['GET'])
def check_status(job_id):
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404
        return jsonify(jobs[job_id])

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    with jobs_lock:
        all_jobs = list(jobs.values())
    
    return jsonify(all_jobs), 200

if __name__ == '__main__':
    print(">> Face Detection API Server Starting...")
    print(f">> Upload folder: {UPLOAD_FOLDER}")
    print(f">> Results folder: {RESULTS_FOLDER}")
    print(f">> No Face folder: {NO_FACE_FOLDER}")
    print(f">> Models loaded successfully")
    print(f">> Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
