// Remove flash messages after 3 seconds
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const flashes = document.querySelectorAll('.alert');
        flashes.forEach(f => {
            f.style.opacity = '0';
            f.style.transition = 'opacity 0.5s';
            setTimeout(() => f.remove(), 500);
        });
    }, 3000);
});
