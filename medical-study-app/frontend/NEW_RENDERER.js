// This is a complete rewrite - replace renderer.js with this content
// See MIGRATION_GUIDE.md for details

const API_BASE = 'http://127.0.0.1:8000/api';
const { ipcRenderer } = require('electron');
const marked = require('marked');

// State
let courses = [];
let currentCourse = null;
let currentLecture = null;
let currentPass = 1;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadCourses();
});

function setupEventListeners() {
    // Course management
    document.getElementById('addCourseBtn').addEventListener('click', () => showModal('addCourseModal'));
    document.getElementById('saveCourseBtn').addEventListener('click', createCourse);
    document.getElementById('cancelCourseBtn').addEventListener('click', () => hideModal('addCourseModal'));
    document.getElementById('backToCoursesBtn').addEventListener('click', showWelcomeScreen);
    
    // Lecture management
    document.getElementById('addLectureBtn').addEventListener('click', () => showModal('addLectureModal'));
    document.getElementById('saveLectureBtn').addEventListener('click', createLecture);
    document.getElementById('cancelLectureBtn').addEventListener('click', () => hideModal('addLectureModal'));
    document.getElementById('backToLecturesBtn').addEventListener('click', () => selectCourse(currentCourse));
    
    // Document upload
    document.getElementById('uploadDocsBtn').addEventListener('click', handleUploadDocuments);
    
    // Study
    document.querySelectorAll('.study-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const pass = parseInt(e.target.dataset.pass);
            startStudy(currentLecture.id, pass);
        });
    });
    document.getElementById('backFromStudyBtn').addEventListener('click', () => showLectureDetail(currentLecture));
    document.getElementById('completePassBtn').addEventListener('click', markPassComplete);
    
    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            hideModal(modal.id);
        });
    });
}

// API Calls
async function loadCourses() {
    try {
        const response = await fetch(`${API_BASE}/courses`);
        const data = await response.json();
        courses = data.courses;
        renderCourses();
        
        if (courses.length === 0) {
            showWelcomeScreen();
        }
    } catch (error) {
        console.error('Error loading courses:', error);
        alert('Error loading courses. Make sure the backend is running.');
    }
}

async function createCourse() {
    const name = document.getElementById('courseNameInput').value.trim();
    const description = document.getElementById('courseDescInput').value.trim();
    
    if (!name) {
        alert('Please enter a course name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/courses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description: description || null })
        });
        
        const data = await response.json();
        if (data.success) {
            hideModal('addCourseModal');
            document.getElementById('courseNameInput').value = '';
            document.getElementById('courseDescInput').value = '';
            await loadCourses();
        }
    } catch (error) {
        alert('Error creating course: ' + error.message);
    }
}

async function createLecture() {
    const title = document.getElementById('lectureNameInput').value.trim();
    const description = document.getElementById('lectureDescInput').value.trim();
    
    if (!title) {
        alert('Please enter a lecture title');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/lectures`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                course_id: currentCourse.id,
                title,
                description: description || null
            })
        });
        
        const data = await response.json();
        if (data.success) {
            hideModal('addLectureModal');
            document.getElementById('lectureNameInput').value = '';
            document.getElementById('lectureDescInput').value = '';
            await loadCourses();
            selectCourse(courses.find(c => c.id === currentCourse.id));
        }
    } catch (error) {
        alert('Error creating lecture: ' + error.message);
    }
}

async function handleUploadDocuments() {
    try {
        const filePaths = await ipcRenderer.invoke('select-files');
        if (!filePaths || filePaths.length === 0) return;
        
        const formData = new FormData();
        for (const filePath of filePaths) {
            const response = await fetch(`file://${filePath}`);
            const blob = await response.blob();
            const filename = filePath.split('/').pop().split('\\').pop();
            formData.append('files', blob, filename);
        }
        
        const uploadResponse = await fetch(`${API_BASE}/lectures/${currentLecture.id}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await uploadResponse.json();
        if (result.success) {
            alert(`Uploaded ${result.uploaded} documents. Extracted ${result.details.uploaded_files.reduce((sum, f) => sum + f.images_extracted, 0)} images.`);
            await loadCourses();
            const lecture = courses.flatMap(c => c.lectures).find(l => l.id === currentLecture.id);
            showLectureDetail(lecture);
        }
    } catch (error) {
        alert('Error uploading documents: ' + error.message);
    }
}

async function startStudy(lectureId, passNumber) {
    currentPass = passNumber;
    showStudyView();
    
    document.getElementById('studyTitle').textContent = currentLecture.title;
    document.getElementById('currentPassBadge').textContent = `Pass ${passNumber}`;
    document.getElementById('summaryContent').innerHTML = '<div class="loading"><div class="spinner"></div><p>Generating summary...</p></div>';
    
    try {
        const response = await fetch(`${API_BASE}/summary/${lectureId}/${passNumber}`);
        const data = await response.json();
        
        const html = marked.parse(data.summary);
        document.getElementById('summaryContent').innerHTML = html;
        
        // Show images if any
        if (data.images && data.images.length > 0) {
            renderImages(data.images);
        } else {
            document.getElementById('imagesGallery').classList.add('hidden');
        }
        
        updateCompleteButton();
    } catch (error) {
        document.getElementById('summaryContent').innerHTML = `<div class="loading" style="color: #e74c3c;">Error: ${error.message}</div>`;
    }
}

async function markPassComplete() {
    try {
        const response = await fetch(`${API_BASE}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lecture_id: currentLecture.id,
                pass_number: currentPass
            })
        });
        
        const result = await response.json();
        if (result.success) {
            alert(`Pass ${currentPass} marked as complete!`);
            await loadCourses();
            updateCompleteButton();
        }
    } catch (error) {
        alert('Error marking pass complete: ' + error.message);
    }
}

// Render Functions
function renderCourses() {
    const container = document.getElementById('coursesList');
    container.innerHTML = '';
    
    if (courses.length === 0) {
        container.innerHTML = '<p class="empty-message">No courses yet. Click "+ Add Course" to get started.</p>';
        return;
    }
    
    courses.forEach(course => {
        const totalLectures = course.lectures.length;
        const completedPasses = course.lectures.reduce((acc, lec) => 
            acc + lec.progress.filter(p => p.completed).length, 0);
        const totalPasses = totalLectures * 3;
        
        const div = document.createElement('div');
        div.className = 'course-item';
        div.innerHTML = `
            <div class="course-name">${course.name}</div>
            <div class="course-stats">${totalLectures} lectures • ${completedPasses}/${totalPasses} passes</div>
        `;
        div.addEventListener('click', () => selectCourse(course));
        container.appendChild(div);
    });
}

function renderImages(images) {
    const gallery = document.getElementById('imagesGallery');
    const grid = document.getElementById('imagesGrid');
    
    gallery.classList.remove('hidden');
    grid.innerHTML = '';
    
    images.forEach((img, index) => {
        // Extract doc_id from path
        const pathParts = img.path.split('/');
        const docFolder = pathParts[pathParts.length - 2]; // e.g., "doc_1"
        const docId = docFolder.split('_')[1];
        const lectureFolder = pathParts[pathParts.length - 3]; // e.g., "lecture_1"
        const lectureId = lectureFolder.split('_')[1];
        
        const imgUrl = `${API_BASE}/images/${lectureId}/${docId}/${img.filename}`;
        
        const imgDiv = document.createElement('div');
        imgDiv.className = 'image-item';
        imgDiv.innerHTML = `
            <img src="${imgUrl}" alt="Image ${index + 1}">
            <div class="image-caption">
                <small>Page ${img.page_number} • ${img.document}</small>
            </div>
        `;
        imgDiv.querySelector('img').addEventListener('click', () => showLightbox(imgUrl, `Page ${img.page_number} - ${img.document}`));
        grid.appendChild(imgDiv);
    });
}

function updateCompleteButton() {
    const progress = currentLecture.progress.find(p => p.pass_number === currentPass);
    const btn = document.getElementById('completePassBtn');
    
    if (progress && progress.completed) {
        btn.textContent = 'Pass Completed ✓';
        btn.disabled = true;
        btn.style.background = '#95a5a6';
    } else {
        btn.textContent = 'Mark Pass Complete ✓';
        btn.disabled = false;
        btn.style.background = '#27ae60';
    }
}

// View Navigation
function showWelcomeScreen() {
    document.getElementById('welcomeScreen').classList.remove('hidden');
    document.getElementById('lecturesView').classList.add('hidden');
    document.getElementById('lectureDetailView').classList.add('hidden');
    document.getElementById('studyView').classList.add('hidden');
    currentCourse = null;
}

function selectCourse(course) {
    currentCourse = course;
    document.getElementById('currentCourseName').textContent = course.name;
    document.getElementById('currentCourseDesc').textContent = course.description || '';
    
    const container = document.getElementById('lecturesList');
    container.innerHTML = '';
    
    if (course.lectures.length === 0) {
        container.innerHTML = '<p class="empty-message">No lectures yet. Click "+ Add Lecture" to create one.</p>';
    } else {
        course.lectures.forEach(lecture => {
            const div = document.createElement('div');
            div.className = 'lecture-card';
            
            const progressHTML = lecture.progress.map(p => {
                const status = p.completed ? 'completed' : 'incomplete';
                return `<span class="progress-badge ${status}">Pass ${p.pass_number}${p.completed ? ' ✓' : ''}</span>`;
            }).join('');
            
            div.innerHTML = `
                <div class="lecture-title">${lecture.title}</div>
                <div class="lecture-subtitle">${lecture.document_count} document${lecture.document_count !== 1 ? 's' : ''}</div>
                <div class="progress-indicators">${progressHTML}</div>
            `;
            div.addEventListener('click', () => showLectureDetail(lecture));
            container.appendChild(div);
        });
    }
    
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('lecturesView').classList.remove('hidden');
    document.getElementById('lectureDetailView').classList.add('hidden');
    document.getElementById('studyView').classList.add('hidden');
}

function showLectureDetail(lecture) {
    currentLecture = lecture;
    document.getElementById('lectureDetailTitle').textContent = lecture.title;
    document.getElementById('lectureDetailDesc').textContent = lecture.description || '';
    
    // Load documents
    fetch(`${API_BASE}/lectures/${lecture.id}/documents`)
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('documentsList');
            container.innerHTML = '';
            
            if (data.documents.length === 0) {
                container.innerHTML = '<p class="empty-message">No documents uploaded yet.</p>';
            } else {
                data.documents.forEach(doc => {
                    const div = document.createElement('div');
                    div.className = 'document-item';
                    div.innerHTML = `
                        <div class="document-icon">📄</div>
                        <div class="document-info">
                            <div class="document-name">${doc.filename}</div>
                            <div class="document-meta">${doc.file_type.toUpperCase()} • ${doc.image_count} images</div>
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
        });
    
    // Update pass cards
    lecture.progress.forEach(p => {
        const card = document.querySelector(`.pass-card[data-pass="${p.pass_number}"]`);
        const status = card.querySelector('.pass-status');
        if (p.completed) {
            status.textContent = '✓ Completed';
            status.style.color = '#27ae60';
        } else {
            status.textContent = '';
        }
    });
    
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('lecturesView').classList.add('hidden');
    document.getElementById('lectureDetailView').classList.remove('hidden');
    document.getElementById('studyView').classList.add('hidden');
}

function showStudyView() {
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('lecturesView').classList.add('hidden');
    document.getElementById('lectureDetailView').classList.add('hidden');
    document.getElementById('studyView').classList.remove('hidden');
}

// Modal functions
function showModal(modalId) {
    document.getElementById('modalOverlay').classList.remove('hidden');
    document.getElementById(modalId).classList.remove('hidden');
}

function hideModal(modalId) {
    document.getElementById('modalOverlay').classList.add('hidden');
    document.getElementById(modalId).classList.add('hidden');
}

function showLightbox(imageUrl, title) {
    document.getElementById('lightboxImage').src = imageUrl;
    document.getElementById('lightboxTitle').textContent = title;
    showModal('imageLightbox');
}
