let currentQuestions = [];
let userAnswers = [];

function uploadDocument() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Selectează un document!');
        return;
    }
    
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('uploadBtn').disabled = true;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentQuestions = data.questions;
            displayQuestions(data.questions);
            document.getElementById('quizSection').classList.remove('hidden');
        } else {
            alert('Eroare: ' + data.error);
        }
    })
    .catch(error => {
        alert('Eroare la conectare: ' + error);
    })
    .finally(() => {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('uploadBtn').disabled = false;
    });
}

function displayQuestions(questions) {
    const container = document.getElementById('questions');
    container.innerHTML = '';
    userAnswers = new Array(questions.length).fill(null);
    
    questions.forEach((q, index) => {
        const qDiv = document.createElement('div');
        qDiv.className = 'question-card';
        qDiv.innerHTML = `
            <h4>Întrebarea ${index + 1}</h4>
            <p>${q.text}</p>
            <div class="options" id="options-${index}">
                ${q.options.map((opt, optIndex) => `
                    <label>
                        <input type="radio" name="q${index}" value="${optIndex}" 
                               onchange="saveAnswer(${index}, ${optIndex})">
                        ${opt}
                    </label>
                `).join('')}
            </div>
        `;
        container.appendChild(qDiv);
    });
}

function saveAnswer(questionIndex, answerIndex) {
    userAnswers[questionIndex] = answerIndex;
    
    // Verifică dacă toate întrebările au răspuns
    const allAnswered = userAnswers.every(a => a !== null);
    document.getElementById('submitBtn').disabled = !allAnswered;
}

function submitAnswers() {
    // Convertim răspunsurile în formatul așteptat de backend (0 = greșit, 1 = corect)
    const answers = userAnswers.map((ans, index) => {
        return ans === currentQuestions[index].correct ? 1 : 0;
    });
    
    document.getElementById('loading').classList.remove('hidden');
    
    fetch('http://localhost:5000/evaluate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answers: answers })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('score').textContent = data.score + '%';
            document.getElementById('level').textContent = data.level.name;
            document.getElementById('confidence').textContent = 
                `(încredere: ${Math.round(data.level.confidence * 100)}%)`;
            document.getElementById('chances').textContent = data.chances + '%';
            
            document.getElementById('resultsSection').classList.remove('hidden');
        } else {
            alert('Eroare: ' + data.error);
        }
    })
    .catch(error => {
        alert('Eroare la conectare: ' + error);
    })
    .finally(() => {
        document.getElementById('loading').classList.add('hidden');
    });
}