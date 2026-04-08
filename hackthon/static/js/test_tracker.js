document.addEventListener("DOMContentLoaded", function () {
    let warnings = 0;
    const MAX_WARNINGS = 3;
    const warningBox = document.getElementById('warningBox');
    const warningCount = document.getElementById('warningCount');
    const warningsInput = document.getElementById('warningsInput');
    const form = document.getElementById('submitTestForm');

    // Timer logic
    let timeRemaining = 15 * 60; // 15 minutes in seconds
    const timerDisplay = document.getElementById('timer');

    const timerInterval = setInterval(function () {
        timeRemaining--;
        let minutes = Math.floor(timeRemaining / 60);
        let seconds = timeRemaining % 60;
        
        minutes = minutes < 10 ? '0' + minutes : minutes;
        seconds = seconds < 10 ? '0' + seconds : seconds;
        
        timerDisplay.textContent = `${minutes}:${seconds}`;

        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            alert("Time's up! Transmitting answers automatically.");
            form.submit();
        }
    }, 1000);

    // Anti-cheating Tab Switch Detection
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            warnings++;
            warningCount.textContent = warnings;
            warningsInput.value = warnings;
            warningBox.style.display = 'block';
            
            // Highlight the timer header temporarily in red
            document.querySelector('.test-header').style.borderColor = 'var(--accent)';
            
            if (warnings >= MAX_WARNINGS) {
                alert("Security breach. System locked. Transmitting answers due to rule violations.");
                form.submit();
            }
        }
    });

    window.submitTest = function() {
        if (confirm("Are you ready to transmit your answers?")) {
            form.submit();
        }
    };
});
