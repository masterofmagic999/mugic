// Mugic - Main Application JavaScript with Authentication

let currentPieceId = null;
let mediaRecorder = null;
let audioChunks = [];
let currentInstrument = null;
let authToken = null;
let currentUser = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Check for stored auth token
    authToken = localStorage.getItem('mugic_auth_token');
    if (authToken) {
        loadUserProfile();
    }
    
    // Load instruments
    loadInstruments();
    
    // Load pieces library
    loadPiecesLibrary();
    
    // Set up event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // File upload
    document.getElementById('sheet-music-file').addEventListener('change', handleFileSelect);
    document.getElementById('upload-btn').addEventListener('click', uploadSheetMusic);
    
    // Recording
    document.getElementById('start-recording-btn').addEventListener('click', startRecording);
    document.getElementById('stop-recording-btn').addEventListener('click', stopRecording);
    
    // Actions
    document.getElementById('practice-again-btn').addEventListener('click', practiceAgain);
    document.getElementById('new-piece-btn').addEventListener('click', uploadNewPiece);
    
    // Authentication
    document.getElementById('login-btn').addEventListener('click', showLoginModal);
    document.getElementById('logout-btn').addEventListener('click', logout);
    document.querySelector('.close-modal').addEventListener('click', closeAuthModal);
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterForm();
    });
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
    });
    
    // Auth forms
    document.getElementById('login-form-element').addEventListener('submit', handleLogin);
    document.getElementById('register-form-element').addEventListener('submit', handleRegister);
    
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('auth-modal');
        if (e.target === modal) {
            closeAuthModal();
        }
    });
}

// ============================================================================
// Authentication Functions
// ============================================================================

function showLoginModal() {
    document.getElementById('auth-modal').style.display = 'block';
    showLoginForm();
}

function closeAuthModal() {
    document.getElementById('auth-modal').style.display = 'none';
}

function showLoginForm() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
}

function showRegisterForm() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        
        const data = await response.json();
        
        if (data.success) {
            authToken = data.tokens.access_token;
            currentUser = data.user;
            localStorage.setItem('mugic_auth_token', authToken);
            
            updateUIForLoggedInUser();
            closeAuthModal();
            alert('Welcome back, ' + currentUser.username + '!');
            loadPiecesLibrary();
        } else {
            alert('Login failed: ' + data.error);
        }
    } catch (error) {
        alert('Login error: ' + error.message);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const fullName = document.getElementById('register-fullname').value;
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username,
                email,
                password,
                full_name: fullName || undefined
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Account created successfully! Please sign in.');
            showLoginForm();
            document.getElementById('login-username').value = username;
        } else {
            alert('Registration failed: ' + data.error);
        }
    } catch (error) {
        alert('Registration error: ' + error.message);
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch('/api/auth/profile', {
            headers: {
                'Authorization': 'Bearer ' + authToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.user;
            updateUIForLoggedInUser();
        } else {
            // Token expired or invalid
            logout();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        logout();
    }
}

function updateUIForLoggedInUser() {
    document.getElementById('login-btn').style.display = 'none';
    document.getElementById('user-menu').style.display = 'flex';
    document.getElementById('username-display').textContent = currentUser.username;
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('mugic_auth_token');
    
    document.getElementById('login-btn').style.display = 'block';
    document.getElementById('user-menu').style.display = 'none';
    
    alert('Logged out successfully');
}

// ============================================================================
// Original Functions (with auth headers added where needed)
// ============================================================================

async function loadInstruments() {
    try {
        const response = await fetch('/api/instruments');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('instrument-select');
            select.innerHTML = '<option value="">Select an instrument</option>';
            
            // Group by category
            const categories = {};
            data.instruments.forEach(inst => {
                if (!categories[inst.category]) {
                    categories[inst.category] = [];
                }
                categories[inst.category].push(inst);
            });
            
            // Add options by category
            Object.keys(categories).forEach(category => {
                const optgroup = document.createElement('optgroup');
                optgroup.label = category.charAt(0).toUpperCase() + category.slice(1);
                
                categories[category].forEach(inst => {
                    const option = document.createElement('option');
                    option.value = inst.id;
                    option.textContent = inst.name;
                    optgroup.appendChild(option);
                });
                
                select.appendChild(optgroup);
            });
        }
    } catch (error) {
        console.error('Error loading instruments:', error);
    }
}

async function loadPiecesLibrary() {
    try {
        const response = await fetch('/api/pieces');
        const data = await response.json();
        
        if (data.success && data.pieces.length > 0) {
            const container = document.getElementById('pieces-list');
            container.innerHTML = '';
            
            data.pieces.forEach(piece => {
                const card = document.createElement('div');
                card.className = 'piece-card';
                card.innerHTML = `
                    <h4>${piece.filename}</h4>
                    <p>Uploaded: ${new Date(piece.upload_date).toLocaleDateString()}</p>
                    <p>Practice sessions: ${piece.session_count}</p>
                `;
                card.addEventListener('click', () => selectPiece(piece.id));
                container.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading pieces:', error);
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('file-name').textContent = file.name;
        document.getElementById('upload-btn').style.display = 'inline-block';
    }
}

async function uploadSheetMusic() {
    const fileInput = document.getElementById('sheet-music-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('upload-status', 'Please select a file first', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showStatus('upload-status', '🎼 Analyzing sheet music...', 'success');
    
    try {
        const response = await fetch('/api/upload-sheet-music', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPieceId = data.piece_id;
            showStatus('upload-status', '✅ Sheet music analyzed successfully!', 'success');
            
            // Show practice section
            document.getElementById('practice-section').style.display = 'block';
            document.getElementById('current-piece-name').textContent = file.name;
            
            const analysis = data.analysis;
            document.getElementById('piece-details').innerHTML = `
                <strong>Time Signature:</strong> ${analysis.time_signature} | 
                <strong>Key:</strong> ${analysis.key_signature} | 
                <strong>Tempo:</strong> ${analysis.tempo} BPM | 
                <strong>Notes:</strong> ${analysis.notes.length}
            `;
            
            // Reload library
            loadPiecesLibrary();
        } else {
            showStatus('upload-status', '❌ Error: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('upload-status', '❌ Upload failed: ' + error.message, 'error');
    }
}

async function selectPiece(pieceId) {
    currentPieceId = pieceId;
    
    // Show practice section
    document.getElementById('practice-section').style.display = 'block';
    document.getElementById('upload-section').style.display = 'none';
    document.getElementById('feedback-section').style.display = 'none';
    
    // Could load piece details here
    showStatus('upload-status', '✅ Piece selected. Ready to practice!', 'success');
}

async function startRecording() {
    const instrumentSelect = document.getElementById('instrument-select');
    currentInstrument = instrumentSelect.value;
    
    if (!currentInstrument) {
        alert('Please select your instrument first');
        return;
    }
    
    if (!currentPieceId) {
        alert('Please upload sheet music first');
        return;
    }
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener('stop', handleRecordingStop);
        
        mediaRecorder.start();
        
        // Update UI
        document.getElementById('start-recording-btn').style.display = 'none';
        document.getElementById('stop-recording-btn').style.display = 'inline-block';
        document.getElementById('recording-status').textContent = '🔴 Recording...';
    } catch (error) {
        alert('Error accessing microphone: ' + error.message);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        
        // Stop all tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        // Update UI
        document.getElementById('start-recording-btn').style.display = 'inline-block';
        document.getElementById('stop-recording-btn').style.display = 'none';
        document.getElementById('recording-status').textContent = '';
    }
}

async function handleRecordingStop() {
    // Create audio blob
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    
    // Create file name
    const timestamp = Date.now();
    const fileName = `recording_${timestamp}.wav`;
    
    // Save audio file (in a real app, you'd upload this)
    // For this demo, we'll simulate the analysis
    
    document.getElementById('analysis-loading').style.display = 'block';
    
    // Simulate analysis (in production, would upload and analyze)
    setTimeout(() => {
        analyzePerformance(fileName);
    }, 2000);
}

async function analyzePerformance(audioFile) {
    try {
        const disableDynamics = document.getElementById('disable-dynamics').checked;
        
        const response = await fetch('/api/analyze-performance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                piece_id: currentPieceId,
                audio_file: audioFile,
                instrument: currentInstrument,
                disable_dynamics: disableDynamics
            })
        });
        
        const data = await response.json();
        
        document.getElementById('analysis-loading').style.display = 'none';
        
        if (data.success) {
            displayFeedback(data.feedback, data.comparison);
        } else {
            alert('Analysis failed: ' + data.error);
        }
    } catch (error) {
        document.getElementById('analysis-loading').style.display = 'none';
        alert('Analysis failed: ' + error.message);
    }
}

function displayFeedback(feedback, comparison) {
    // Hide practice section, show feedback
    document.getElementById('practice-section').style.display = 'none';
    document.getElementById('feedback-section').style.display = 'block';
    
    // Overall score
    document.getElementById('overall-score').textContent = feedback.overall_score;
    document.getElementById('performance-summary').textContent = feedback.summary;
    
    // Pitch feedback
    displayScoreCard('pitch', feedback.pitch);
    
    // Rhythm feedback
    displayScoreCard('rhythm', feedback.rhythm);
    
    // Tempo feedback
    displayScoreCard('tempo', feedback.tempo);
    
    // Dynamics feedback
    if (feedback.dynamics) {
        document.getElementById('dynamics-card').style.display = 'block';
        displayScoreCard('dynamics', feedback.dynamics);
    } else {
        document.getElementById('dynamics-card').style.display = 'none';
    }
    
    // Recommendations
    const recList = document.getElementById('recommendations-list');
    recList.innerHTML = '';
    feedback.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recList.appendChild(li);
    });
    
    // Comparison
    if (comparison && comparison.has_previous) {
        document.getElementById('comparison-section').style.display = 'block';
        const compContent = document.getElementById('comparison-content');
        compContent.innerHTML = `
            <p><strong>${comparison.message}</strong></p>
            <p>Previous score: ${comparison.previous_score}/100 → Current score: ${comparison.current_score}/100</p>
            <p>Total attempts: ${comparison.total_attempts}</p>
            <div style="margin-top: 15px;">
                <strong>✅ Improvements:</strong>
                <ul>
                    ${comparison.improvements.map(imp => `<li>${imp}</li>`).join('')}
                </ul>
            </div>
            <div style="margin-top: 15px;">
                <strong>📝 Areas to focus on:</strong>
                <ul>
                    ${comparison.needs_work.map(work => `<li>${work}</li>`).join('')}
                </ul>
            </div>
        `;
    }
}

function displayScoreCard(category, data) {
    const scoreBar = document.getElementById(`${category}-score-bar`);
    const scoreText = document.getElementById(`${category}-score`);
    const details = document.getElementById(`${category}-details`);
    
    scoreBar.style.width = data.score + '%';
    scoreText.textContent = `Score: ${data.score}/100`;
    
    // Add details based on category
    let detailsHTML = '';
    
    if (category === 'pitch' && data.errors) {
        if (data.errors.length > 0) {
            detailsHTML = `<p style="margin-top: 10px;">Correct notes: ${data.correct_notes}/${data.total_notes}</p>`;
        }
    } else if (category === 'tempo') {
        detailsHTML = `
            <p style="margin-top: 10px;">
                Expected: ${data.expected_bpm} BPM<br>
                Your tempo: ${data.actual_bpm} BPM<br>
                Rating: ${data.rating}
            </p>
        `;
    }
    
    details.innerHTML = detailsHTML;
}

function practiceAgain() {
    // Reset to practice section
    document.getElementById('feedback-section').style.display = 'none';
    document.getElementById('practice-section').style.display = 'block';
}

function uploadNewPiece() {
    // Reset everything
    currentPieceId = null;
    document.getElementById('feedback-section').style.display = 'none';
    document.getElementById('practice-section').style.display = 'none';
    document.getElementById('upload-section').style.display = 'block';
    document.getElementById('sheet-music-file').value = '';
    document.getElementById('file-name').textContent = '';
    document.getElementById('upload-btn').style.display = 'none';
}

function showStatus(elementId, message, type) {
    const statusEl = document.getElementById(elementId);
    statusEl.textContent = message;
    statusEl.className = 'status-message ' + type;
}
