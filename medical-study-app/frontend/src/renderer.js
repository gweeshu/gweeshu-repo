const { ipcRenderer } = require('electron');
const { marked } = require('marked');

const API_BASE = 'http://127.0.0.1:8000/api';

let currentSubjects = [];
let currentLecture = null;
let currentPass = 1;

// Elements
const uploadBtn = document.getElementById('uploadBtn');
const refreshBtn = document.getElementById('refreshBtn');
const subjectsList = document.getElementById('subjectsList');
const welcomeScreen = document.getElementById('welcomeScreen');
const lecturesView = document.getElementById('lecturesView');
const studyView = document.getElementById('studyView');
const currentSubjectEl = document.getElementById('currentSubject');
const lecturesList = document.getElementById('lecturesList');
const backBtn = document.getElementById('backBtn');
const studyTitle = document.getElementById('studyTitle');
const summaryContent = document.getElementById('summaryContent');
const completeBtn = document.getElementById('completeBtn');

// Event listeners
uploadBtn.addEventListener('click', handleUpload);
refreshBtn.addEventListener('click', loadSubjects);
backBtn.addEventListener('click', showLecturesView);
completeBtn.addEventListener('click', markPassComplete);

// Pass selector buttons
document.querySelectorAll('.pass-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const pass = parseInt(e.target.dataset.pass);
        selectPass(pass);
    });
});

// Initialize
loadSubjects();

async function handleUpload() {
    try {
        // Open file dialog
        const filePaths = await ipcRenderer.invoke('select-files');

        if (!filePaths || filePaths.length === 0) {
            return;
        }

        uploadBtn.textContent = 'Processing...';
        uploadBtn.disabled = true;

        // Create FormData
        const formData = new FormData();
        for (const filePath of filePaths) {
            const response = await fetch(`file://${filePath}`);
            const blob = await response.blob();
            const filename = filePath.split('/').pop().split('\\').pop();
            formData.append('files', blob, filename);
        }

        // Upload to API
        const uploadResponse = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await uploadResponse.json();

        if (result.success) {
            alert(`Success! Processed ${result.details.processed} documents.\nSubjects: ${result.details.subjects_created.join(', ')}`);
            loadSubjects();
        } else {
            alert('Upload failed: ' + result.message);
        }

    } catch (error) {
        alert('Error uploading files: ' + error.message);
        console.error(error);
    } finally {
        uploadBtn.textContent = 'Upload Documents';
        uploadBtn.disabled = false;
    }
}

async function loadSubjects() {
    try {
        const response = await fetch(`${API_BASE}/subjects`);
        const data = await response.json();
        currentSubjects = data.subjects;

        renderSubjects();

        if (currentSubjects.length === 0) {
            showWelcomeScreen();
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
        alert('Error loading subjects. Make sure the backend server is running.');
    }
}

function renderSubjects() {
    subjectsList.innerHTML = '';

    if (currentSubjects.length === 0) {
        subjectsList.innerHTML = '<p style="color: #999; font-size: 0.9rem;">No subjects yet. Upload documents to get started.</p>';
        return;
    }

    currentSubjects.forEach(subject => {
        const totalLectures = subject.lectures.length;
        const completedPasses = subject.lectures.reduce((acc, lecture) => {
            return acc + lecture.progress.filter(p => p.completed).length;
        }, 0);
        const totalPasses = totalLectures * 3;

        const div = document.createElement('div');
        div.className = 'subject-item';
        div.innerHTML = `
            <div class="subject-name">${subject.name}</div>
            <div class="subject-stats">${totalLectures} lectures • ${completedPasses}/${totalPasses} passes</div>
        `;
        div.addEventListener('click', () => selectSubject(subject));
        subjectsList.appendChild(div);
    });
}

function selectSubject(subject) {
    showLecturesView();
    currentSubjectEl.textContent = subject.name;

    // Highlight selected subject
    document.querySelectorAll('.subject-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.subject-item').classList.add('active');

    // Render lectures
    lecturesList.innerHTML = '';

    if (subject.lectures.length === 0) {
        lecturesList.innerHTML = '<p>No lectures in this subject yet.</p>';
        return;
    }

    subject.lectures.forEach(lecture => {
        const div = document.createElement('div');
        div.className = 'lecture-card';

        const progressHTML = lecture.progress.map(p => {
            const status = p.completed ? 'completed' : 'incomplete';
            const label = p.completed ? `Pass ${p.pass_number} ✓` : `Pass ${p.pass_number}`;
            return `<span class="progress-badge ${status}">${label}</span>`;
        }).join('');

        div.innerHTML = `
            <div class="lecture-title">${lecture.title}</div>
            <div class="lecture-filename">${lecture.filename}</div>
            <div class="progress-indicators">${progressHTML}</div>
        `;

        div.addEventListener('click', () => openLecture(lecture));
        lecturesList.appendChild(div);
    });
}

function openLecture(lecture) {
    currentLecture = lecture;
    showStudyView();
    studyTitle.textContent = lecture.title;

    // Find first incomplete pass or default to pass 1
    const firstIncomplete = lecture.progress.find(p => !p.completed);
    currentPass = firstIncomplete ? firstIncomplete.pass_number : 1;

    selectPass(currentPass);
}

async function selectPass(passNumber) {
    currentPass = passNumber;

    // Update button states
    document.querySelectorAll('.pass-btn').forEach(btn => {
        btn.classList.remove('active');
        if (parseInt(btn.dataset.pass) === passNumber) {
            btn.classList.add('active');
        }
    });

    // Check if pass is completed
    const progress = currentLecture.progress.find(p => p.pass_number === passNumber);
    if (progress && progress.completed) {
        completeBtn.textContent = 'Pass Completed ✓';
        completeBtn.disabled = true;
        completeBtn.style.background = '#95a5a6';
    } else {
        completeBtn.textContent = 'Mark Pass Complete';
        completeBtn.disabled = false;
        completeBtn.style.background = '#27ae60';
    }

    // Load summary
    await loadSummary(currentLecture.id, passNumber);
}

async function loadSummary(lectureId, passNumber) {
    summaryContent.innerHTML = '<div class="loading">Generating summary with Claude...</div>';

    try {
        const response = await fetch(`${API_BASE}/summary/${lectureId}/${passNumber}`);
        const data = await response.json();

        // Convert markdown to HTML
        const html = marked.parse(data.summary);
        summaryContent.innerHTML = html;

    } catch (error) {
        summaryContent.innerHTML = `<div class="loading" style="color: #e74c3c;">Error loading summary: ${error.message}</div>`;
        console.error(error);
    }
}

async function markPassComplete() {
    try {
        const response = await fetch(`${API_BASE}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lecture_id: currentLecture.id,
                pass_number: currentPass
            })
        });

        const result = await response.json();

        if (result.success) {
            // Update local state
            const progress = currentLecture.progress.find(p => p.pass_number === currentPass);
            if (progress) {
                progress.completed = true;
                progress.completed_at = new Date().toISOString();
            }

            // Update UI
            completeBtn.textContent = 'Pass Completed ✓';
            completeBtn.disabled = true;
            completeBtn.style.background = '#95a5a6';

            // Reload subjects to update counts
            loadSubjects();

            alert(`Pass ${currentPass} marked as complete!`);
        }
    } catch (error) {
        alert('Error marking pass complete: ' + error.message);
        console.error(error);
    }
}

function showWelcomeScreen() {
    welcomeScreen.classList.remove('hidden');
    lecturesView.classList.add('hidden');
    studyView.classList.add('hidden');
}

function showLecturesView() {
    welcomeScreen.classList.add('hidden');
    lecturesView.classList.remove('hidden');
    studyView.classList.add('hidden');
}

function showStudyView() {
    welcomeScreen.classList.add('hidden');
    lecturesView.classList.add('hidden');
    studyView.classList.remove('hidden');
}
