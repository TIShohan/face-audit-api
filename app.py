"""
Face Detection API - Flask Backend
Converts the Jupyter notebook face detection logic into a web service
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
import requests
import cv2
import mediapipe as mp
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

# Processing configuration
DOWNLOAD_TIMEOUT = 20
MEDIAPIPE_CONF_THRESH = 0.80
DNN_CONF_THRESH = 0.70
NUM_THREADS = 6
BATCH_SIZE = 100  # Smaller batches for web to give more frequent updates

# Global job storage (in production, use Redis or database)
jobs = {}
jobs_lock = threading.Lock()

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

def download_image(url):
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except:
        return None

def detect_with_dnn(image):
    """Detect face using OpenCV DNN"""
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    return np.max(detections[0, 0, :, 2]) > DNN_CONF_THRESH

def process_row(row, job_id):
    """Process a single row for face detection"""
    img_url = row.get("Check-In Photo")
    id_val = row.get("id", row.name)

    if pd.isna(img_url) or str(img_url).strip() == "":
        return row.name, "Skipped (empty URL)", ""

    image = download_image(str(img_url))

    if image is None:
        return row.name, "DOWNLOAD_ERROR", "Image could not be downloaded"

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # MediaPipe detection
    with mp_face_detection.FaceDetection(min_detection_confidence=MEDIAPIPE_CONF_THRESH) as face_detector:
        results = face_detector.process(image_rgb)
        face_found = results.detections is not None and len(results.detections) > 0

    # Fallback to DNN if MediaPipe fails
    if not face_found:
        face_found = detect_with_dnn(image)

    if face_found:
        return row.name, "GOOD", ""
    else:
        # Save NO FACE image
        job_folder = os.path.join(NO_FACE_FOLDER, job_id)
        os.makedirs(job_folder, exist_ok=True)
        save_path = os.path.join(job_folder, f"{id_val}_NOFACE.jpg")
        cv2.imwrite(save_path, image)
        return row.name, "NO FACE", f"Saved: {save_path}"

def process_csv_job(job_id, csv_path, original_filename):
    """Background job to process CSV file"""
    try:
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
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            future_to_idx = {
                executor.submit(process_row, row, job_id): original_idx
                for original_idx, row in df.loc[processing_indices].iterrows()
            }
            
            for future in as_completed(future_to_idx):
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
        
        # Save results
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
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    filename = f"{job_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Initialize job
    with jobs_lock:
        jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'original_filename': file.filename,
            'uploaded_at': datetime.now().isoformat(),
            'total_rows': 0,
            'rows_to_process': 0,
            'processed': 0,
            'good_count': 0,
            'noface_count': 0,
            'download_error_count': 0
        }
    
    # Start background processing
    thread = threading.Thread(target=process_csv_job, args=(job_id, filepath, file.filename))
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
    """Download NO FACE images as ZIP"""
    job_folder = os.path.join(NO_FACE_FOLDER, job_id)
    
    if not os.path.exists(job_folder):
        return jsonify({'error': 'No images found'}), 404
    
    # Create ZIP in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(job_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zf.write(file_path, arcname=file)
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'noface_images_{job_id}.zip'
    )

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    with jobs_lock:
        all_jobs = list(jobs.values())
    
    return jsonify(all_jobs), 200

if __name__ == '__main__':
    print("🚀 Face Detection API Server Starting...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📁 Results folder: {RESULTS_FOLDER}")
    print(f"📁 No Face folder: {NO_FACE_FOLDER}")
    print(f"🤖 Models loaded successfully")
    print(f"🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
