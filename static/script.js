document.addEventListener('DOMContentLoaded', function() {
    console.log('Log Analyzer frontend is ready!');
    
    // Simple example of adding interactivity
    const heading = document.querySelector('h1');
    heading.addEventListener('click', function() {
        alert('Welcome to the Log Analyzer!');
    });
});