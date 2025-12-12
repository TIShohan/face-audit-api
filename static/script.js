// ==========================================
// FACE DETECTION AUDIT SYSTEM - JAVASCRIPT
// Client-side logic for file upload and processing
// ==========================================

const API_BASE = window.location.origin;
let currentJobId = null;
let statusCheckInterval = null;

// ==========================================
// DOM ELEMENTS
// ==========================================

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadBtn = document.getElementById('uploadBtn');
const loadingOverlay = document.getElementById('loadingOverlay');

const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');

const currentJobName = document.getElementById('currentJobName');
const progressText = document.getElementById('progressText');
const progressPercentage = document.getElementById('progressPercentage');
const progressBar = document.getElementById('progressBar');
const goodCount = document.getElementById('goodCount');
const nofaceCount = document.getElementById('nofaceCount');
const errorCount = document.getElementById('errorCount');

const downloadCsvBtn = document.getElementById('downloadCsvBtn');
const downloadImagesBtn = document.getElementById('downloadImagesBtn');
const downloadProgressBtn = document.getElementById('downloadProgressBtn');
const newJobBtn = document.getElementById('newJobBtn');
const resultsSummary = document.getElementById('resultsSummary');

const jobsList = document.getElementById('jobsList');
const activeJobs = document.getElementById('activeJobs');
const configToggle = document.getElementById('configToggle');
const configPanel = document.getElementById('configPanel');

// ==========================================
// CONFIGURATION HANDLING
// ==========================================

if (configToggle && configPanel) {
    configToggle.addEventListener('click', () => {
        configToggle.classList.toggle('active');
        const isVisible = configPanel.style.display === 'block';
        configPanel.style.display = isVisible ? 'none' : 'block';
    });
}

// ==========================================
// FILE UPLOAD HANDLING
// ==========================================

// Click to browse
browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File selection
fileInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0]);
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
        handleFileSelect(file);
    } else {
        alert('Please upload a CSV file');
    }
});

function handleFileSelect(file) {
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
        alert('Please select a CSV file');
        return;
    }

    // Display file info
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    // Show file info, hide upload content
    document.querySelector('.upload-content').style.display = 'none';
    fileInfo.style.display = 'flex';

    // Store file for upload
    fileInput.files = createFileList(file);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function createFileList(file) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    return dataTransfer.files;
}

// ==========================================
// UPLOAD AND PROCESSING
// ==========================================

uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    // Show loading overlay
    loadingOverlay.style.display = 'flex';

    const formData = new FormData();
    formData.append('file', file);

    // Append Configuration Parameters
    formData.append('download_timeout', document.getElementById('downloadTimeout').value);
    formData.append('mediapipe_thresh', document.getElementById('mpThresh').value);
    formData.append('dnn_thresh', document.getElementById('dnnThresh').value);
    formData.append('num_threads', document.getElementById('numThreads').value);
    formData.append('batch_size', document.getElementById('batchSize').value);
    formData.append('save_images', document.getElementById('saveImages').checked);

    try {
        const response = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            currentJobId = data.job_id;

            // Save to LocalStorage for crash recovery
            localStorage.setItem('activeJobId', currentJobId);
            localStorage.setItem('activeJobName', file.name);

            // Hide upload section, show processing section
            uploadSection.style.display = 'none';
            processingSection.style.display = 'block';
            resultsSection.style.display = 'none';

            currentJobName.textContent = file.name;

            // Start status checking
            startStatusChecking();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload file. Please try again.');
    } finally {
        loadingOverlay.style.display = 'none';
    }
});

// ==========================================
// STATUS CHECKING
// ==========================================

function startStatusChecking() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }

    // Check immediately
    checkJobStatus();

    // Then check every 2 seconds
    statusCheckInterval = setInterval(checkJobStatus, 2000);
}

async function checkJobStatus() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`${API_BASE}/api/status/${currentJobId}`);

        // Handle 404 (Job might be expired/deleted if server restarted)
        if (response.status === 404) {
            clearInterval(statusCheckInterval);
            localStorage.removeItem('activeJobId');
            localStorage.removeItem('activeJobName');
            alert('This job session has expired or was lost (Server Restart). Please upload again.');
            resetToUpload();
            return;
        }

        const data = await response.json();

        if (response.ok) {
            updateProcessingUI(data);

            if (data.status === 'completed') {
                clearInterval(statusCheckInterval);
                // Don't clear LocalStorage yet, user might refresh on results page
                showResults(data);
            } else if (data.status === 'failed') {
                clearInterval(statusCheckInterval);
                alert('Processing failed: ' + (data.error || 'Unknown error'));
                localStorage.removeItem('activeJobId'); // Clear on fail
                resetToUpload();
            }
        }
    } catch (error) {
        console.error('Status check error:', error);
    }
}

function updateProcessingUI(data) {
    const processed = data.processed || 0;
    const total = data.rows_to_process || 0;
    const progress = data.progress || 0;

    progressText.textContent = `${processed} / ${total} images processed`;
    progressPercentage.textContent = `${Math.round(progress)}%`;
    progressBar.style.width = `${progress}%`;

    goodCount.textContent = data.good_count || 0;
    nofaceCount.textContent = data.noface_count || 0;
    errorCount.textContent = data.download_error_count || 0;
}

function showResults(data) {
    processingSection.style.display = 'none';
    resultsSection.style.display = 'block';

    const total = data.rows_to_process || 0;
    const good = data.good_count || 0;
    const noface = data.noface_count || 0;
    const errors = data.download_error_count || 0;

    resultsSummary.textContent = `Processed ${total} images: ${good} with faces, ${noface} without faces, ${errors} errors`;

    // Hide/Show Download Images button based on config
    // Note: status check endpoint generally returns config now? 
    // If not, we might assume true, but for robust UI we usually need to pass it back.
    // For now, let's just show it always unless we know for sure. 
    // Actually, let's keep it simple: if noface_count is 0, arguably we shouldn't show it anyway.
    // But specific to the "Save Images" setting:
    if (data.config && data.config.save_images === false) {
        downloadImagesBtn.style.display = 'none';
        // Also hide partial download images if we had one (we don't yet)
    } else {
        downloadImagesBtn.style.display = 'inline-flex';
    }

    // Load jobs history
    loadJobsHistory();
}

// ==========================================
// DOWNLOAD RESULTS
// ==========================================

downloadCsvBtn.addEventListener('click', () => {
    if (currentJobId) {
        window.location.href = `${API_BASE}/api/download/${currentJobId}`;
    }
});

if (downloadProgressBtn) {
    downloadProgressBtn.addEventListener('click', () => {
        if (currentJobId) {
            window.location.href = `${API_BASE}/api/download/${currentJobId}`;
        }
    });
}

const cancelJobBtn = document.getElementById('cancelJobBtn');
if (cancelJobBtn) {
    cancelJobBtn.addEventListener('click', async () => {
        if (!currentJobId) return;

        if (!confirm('Are you sure you want to cancel this job? Partial results will be saved.')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/api/cancel/${currentJobId}`, {
                method: 'POST'
            });
            const data = await response.json();

            if (response.ok) {
                alert('Job cancelled successfully.');
                if (statusCheckInterval) clearInterval(statusCheckInterval);
                resetToUpload();
            } else {
                alert('Failed to cancel job: ' + data.error);
            }
        } catch (error) {
            console.error('Cancel error:', error);
            alert('Error cancelling job');
        }
    });
}

downloadImagesBtn.addEventListener('click', () => {
    if (currentJobId) {
        window.location.href = `${API_BASE}/api/download-noface/${currentJobId}`;
    }
});

newJobBtn.addEventListener('click', () => {
    resetToUpload();
});

function resetToUpload() {
    currentJobId = null;
    localStorage.removeItem('activeJobId');
    localStorage.removeItem('activeJobName');

    fileInput.value = '';

    uploadSection.style.display = 'block';
    processingSection.style.display = 'none';
    resultsSection.style.display = 'none';

    document.querySelector('.upload-content').style.display = 'block';
    fileInfo.style.display = 'none';

    // Reset progress
    progressBar.style.width = '0%';
    progressPercentage.textContent = '0%';
    progressText.textContent = '0 / 0 images processed';
    goodCount.textContent = '0';
    nofaceCount.textContent = '0';
    errorCount.textContent = '0';
}

// ==========================================
// JOBS HISTORY
// ==========================================

async function loadJobsHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/jobs`);
        const jobs = await response.json();

        if (jobs.length === 0) {
            jobsList.innerHTML = `
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M9 11l3 3L22 4"/>
                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                    </svg>
                    <p>No jobs yet. Upload a CSV file to get started!</p>
                </div>
            `;
            activeJobs.textContent = '0';
            return;
        }

        // Count active jobs
        const active = jobs.filter(j => j.status === 'processing' || j.status === 'queued').length;
        activeJobs.textContent = active;

        // Sort by upload time (newest first)
        jobs.sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at));

        jobsList.innerHTML = jobs.map(job => createJobItem(job)).join('');

    } catch (error) {
        console.error('Failed to load jobs:', error);
    }
}

function createJobItem(job) {
    const statusClass = job.status === 'completed' ? 'completed' :
        job.status === 'processing' || job.status === 'queued' ? 'processing' :
            'failed';

    const uploadTime = new Date(job.uploaded_at).toLocaleString();

    const stats = job.status === 'completed' ?
        `${job.good_count || 0} good, ${job.noface_count || 0} no face, ${job.download_error_count || 0} errors` :
        job.status === 'processing' ?
            `${job.processed || 0} / ${job.rows_to_process || 0} processed` :
            '';

    return `
        <div class="job-item">
            <div class="job-info">
                <h4>${job.original_filename}</h4>
                <div class="job-meta">
                    <span>📅 ${uploadTime}</span>
                    ${stats ? `<span>📊 ${stats}</span>` : ''}
                </div>
            </div>
            <div class="job-status ${statusClass}">${job.status}</div>
        </div>
    `;
}

// ==========================================
// INITIALIZATION
// ==========================================

// Load jobs on page load
document.addEventListener('DOMContentLoaded', () => {
    loadJobsHistory();
    checkForActiveJob();

    // Refresh jobs every 10 seconds
    setInterval(loadJobsHistory, 10000);
});

function checkForActiveJob() {
    const savedJobId = localStorage.getItem('activeJobId');
    const savedJobName = localStorage.getItem('activeJobName');

    if (savedJobId) {
        console.log('Restoring active job:', savedJobId);
        currentJobId = savedJobId;

        // Restore UI state
        uploadSection.style.display = 'none';
        processingSection.style.display = 'block';
        resultsSection.style.display = 'none';

        if (savedJobName) {
            currentJobName.textContent = savedJobName;
        }

        // Resume status checking
        startStatusChecking();
    }
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

function showNotification(message, type = 'info') {
    // Simple notification (can be enhanced with a toast library)
    console.log(`[${type.toUpperCase()}] ${message}`);
}
