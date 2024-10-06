const cpuLoadData = [];
const ramUsageData = [];
const serverNames = [];

// Color palette for the bars
const colors = ['#E60000', '#32CD32', '#0000FF']; // Red, Orange, Green

// Function to fetch server data
function fetchServerData() {
    fetch('/admin_panel/full_server_status')
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
        })
        .catch(error => console.error('Error fetching server data:', error));
}

// Function to update charts with fetched data
function updateCharts(data) {
    // Clear existing data
    cpuLoadData.length = 0;
    ramUsageData.length = 0;
    serverNames.length = 0;

    // Assuming the JSON object has server names as keys
    for (const server in data) {
        if (data.hasOwnProperty(server)) {
            serverNames.push(server);
            cpuLoadData.push(data[server].cpu);
            ramUsageData.push(data[server].ram);
        }
    }

    // Redraw the charts with new data
    drawChart('cpuLoadChart', cpuLoadData, 'Нагрузка ЦП');
    drawChart('ramUsageChart', ramUsageData, 'Оперативная память');
}

// Function to draw the chart
function drawChart(canvasId, data, label) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const barWidth = (width / data.length) - 10;

    ctx.clearRect(0, 0, width, height); // Clear the canvas

    // Draw the label at the top
    ctx.fillStyle = '#333';
    ctx.font = '18px Arial';
    ctx.fillText(label, width / 2 - ctx.measureText(label).width / 2, 20);

    // Draw the bars
    data.forEach((value, index) => {
        const barHeight = (height / 100) * value; // Calculate height based on value
        ctx.fillStyle = colors[index % colors.length]; // Cycle through colors
        ctx.fillRect(index * (barWidth + 10), height - barHeight, barWidth, barHeight);

        // Add value labels
        ctx.fillStyle = '#333';
        ctx.font = '14px Arial';
        ctx.fillText(serverNames[index] + ' ' + value + '%', index * (barWidth + 10) + 5, height - barHeight - 5);
        
        // Add server name labels
        //ctx.fillText(serverNames[index], index * (barWidth + 10) + 5, height - 20);
    });
}

// Fetch server data every 5 seconds
setInterval(fetchServerData, 5000);

// Initial fetch
fetchServerData();