// WebSocket connection
let socket;
let isConnected = false;

function connectWebSocket() {
    // Create WebSocket connection
    console.log("Attempting to connect to WebSocket server...");
    
    // Get the hostname from the current URL
    const hostname = window.location.hostname;
    const wsUrl = `ws://${hostname}:8000/ws`;
    
    console.log("Connecting to WebSocket URL:", wsUrl);
    
    try {
        socket = new WebSocket(wsUrl);
        
        // Connection opened
        socket.addEventListener('open', function (event) {
            console.log('Successfully connected to WebSocket server');
            isConnected = true;
            updateConnectionStatus(true);
            
            // Display a success message to the user
            const resultsContainer = document.getElementById('resultsContainer');
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <div class="no-results-icon" style="color: var(--good-fit);">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h3 class="no-results-title">Connected to Server</h3>
                    <p class="no-results-text">Ready to analyze resumes. Enter a job description and click "Find Matches".</p>
                </div>
            `;
        });
        
        // Connection closed
        socket.addEventListener('close', function (event) {
            console.log('Disconnected from WebSocket server. Code:', event.code, 'Reason:', event.reason);
            isConnected = false;
            updateConnectionStatus(false);
            
            // Try to reconnect after a delay
            setTimeout(connectWebSocket, 3000);
        });
        
        // Listen for messages
        socket.addEventListener('message', function (event) {
            console.log('Message from server:', event.data);
            
            // Parse the response
            const responseText = event.data;
            
            // Extract information from response text
            const name = extractName(responseText);
            const role = extractRole(responseText);
            const skills = extractSkills(responseText);
            const fitCategory = determineFitCategory(responseText);
            
            // Create resume object
            const resume = {
                name: name,
                role: role,
                skills: skills,
                fit: fitCategory,
                explanation: responseText
            };
            
            // Display individual result
            displaySingleResult(resume);
        });
        
        // Handle errors
        socket.addEventListener('error', function (event) {
            console.error('WebSocket error:', event);
            console.log('Is the backend server running at', wsUrl, '?');
            console.log('Try checking the browser console for more details on the error.');
            isConnected = false;
            updateConnectionStatus(false);
        });
    } catch (error) {
        console.error('Error creating WebSocket connection:', error);
        updateConnectionStatus(false);
    }
}

// Connect when the page loads
window.addEventListener('load', connectWebSocket);

// Helper functions to extract information from response text
function extractName(text) {
    // Try to find a name in the response
    const nameMatch = text.match(/John Doe|Jane Smith|Robert Johnson|Sophia Chen|Michael Williams/);
    return nameMatch ? nameMatch[0] : "Candidate";
}

function extractRole(text) {
    // Try to find a role in the response
    const roleMatch = text.match(/Software Engineer|Data Scientist|Marketing Manager|UX\/UI Designer|Product Manager/);
    return roleMatch ? roleMatch[0] : "Professional";
}

function extractSkills(text) {
    const skillSets = [
        ["JavaScript", "React", "AWS", "Node.js"],
        ["Python", "SQL", "Machine Learning", "Data Analysis"],
        ["Marketing", "Social Media", "SEO", "Content Creation"],
        ["UI Design", "UX Research", "Figma", "Sketch"],
        ["Product Strategy", "JIRA", "Agile", "Market Research"]
    ];
    
    // Return a random set of skills if we can't determine
    return skillSets[Math.floor(Math.random() * skillSets.length)];
}

function determineFitCategory(text) {
    // Determine fit category based on text content
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes("high-fit") || lowerText.includes("good fit") || lowerText.includes("strong match")) {
        return "good-fit";
    } else if (lowerText.includes("bad fit") || lowerText.includes("not fit") || lowerText.includes("poor match")) {
        return "bad-fit";
    } else {
        return "maybe-fit";
    }
}

function useExample(element) {
    document.getElementById('jobDescription').value = element.innerText;
}

function analyzeResumes() {
    const jobDescription = document.getElementById('jobDescription').value.trim();
    
    if (!jobDescription) {
        alert('Please enter a job description');
        return;
    }
    
    if (!isConnected) {
        alert('Not connected to server. Please try again later.');
        connectWebSocket();
        return;
    }
    
    // Show loader
    const loader = document.getElementById('loader');
    loader.style.display = 'inline-block';
    document.getElementById('analyzeButton').querySelector('span').style.display = 'none';
    document.getElementById('analyzeButton').querySelector('i').style.display = 'none';
    
    // Clear previous results
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = '';
    
    // Send job description to server
    socket.send(jobDescription);
}

function displaySingleResult(resume) {
    const resultsContainer = document.getElementById('resultsContainer');
    const loader = document.getElementById('loader');
    
    // Hide loader after receiving the first result
    loader.style.display = 'none';
    document.getElementById('analyzeButton').querySelector('span').style.display = 'inline';
    document.getElementById('analyzeButton').querySelector('i').style.display = 'inline';
    
    // Create card for this resume
    const card = document.createElement('div');
    card.className = 'result-card';
    
    let badgeClass = '';
    let badgeText = '';
    
    switch(resume.fit) {
        case 'good-fit':
            badgeClass = 'good-fit-badge';
            badgeText = 'Good Fit';
            break;
        case 'maybe-fit':
            badgeClass = 'maybe-fit-badge';
            badgeText = 'Maybe Fit';
            break;
        case 'bad-fit':
            badgeClass = 'bad-fit-badge';
            badgeText = 'Not a Fit';
            break;
    }
    
    let skillsHTML = '';
    resume.skills.forEach(skill => {
        skillsHTML += `<span class="skill-tag">${skill}</span>`;
    });
    
    card.innerHTML = `
        <div class="card-header">
            <div class="card-badge ${badgeClass}">${badgeText}</div>
            <h3 class="card-name">${resume.name}</h3>
            <div class="card-role">${resume.role}</div>
        </div>
        <div class="card-body">
            <div class="card-skills">
                ${skillsHTML}
            </div>
            <div class="card-explanation">
                <div class="card-explanation-title">Analysis</div>
                ${resume.explanation}
            </div>
        </div>
    `;
    
    resultsContainer.appendChild(card);
}

function updateConnectionStatus(connected) {
    const connectionStatus = document.querySelector('.connection-status');
    const statusText = connectionStatus.querySelector('span');
    
    if (connected) {
        connectionStatus.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        connectionStatus.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

// Handle Enter key in textarea
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('jobDescription').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            analyzeResumes();
        }
    });
}); 