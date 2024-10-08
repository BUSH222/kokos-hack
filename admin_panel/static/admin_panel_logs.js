document.addEventListener("DOMContentLoaded", function() {
    const logsDiv = document.getElementById('logs');

    function updateLogs() {
        fetch('/admin_panel/logs/get_logs')
            .then(response => response.json())
            .then(data => {
                logsDiv.innerHTML = data.map(log => log[0]).join('\n');
            })
            .catch(error => console.error('Error fetching logs:', error));
    }

    // Update logs on page load
    updateLogs();

    // Update logs every 5 seconds
    setInterval(updateLogs, 5000);
});