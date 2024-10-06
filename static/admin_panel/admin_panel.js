const cpuLoadData = {};
const ramUsageData = {};
const serverNames = [];

const colors = ['#E60000', '#32CD32', '#0000FF']

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
    // Update server names
    serverNames.length = 0;
    for (const server in data) {
        if (data.hasOwnProperty(server)) {
            serverNames.push(server);
            if (!cpuLoadData[server]) {
                cpuLoadData[server] = [];
                ramUsageData[server] = [];
            }
            cpuLoadData[server].push(data[server].cpu);
            ramUsageData[server].push(data[server].ram);

            // Limit to 10 data points
            if (cpuLoadData[server].length > 10) cpuLoadData[server].shift();
            if (ramUsageData[server].length > 10) ramUsageData[server].shift();
        }
    }

    // Redraw the charts with new data
    drawChart(cpuLoadChart, cpuLoadData, 'Нагрузка ЦП, %');
    drawChart(ramUsageChart, ramUsageData, 'Оперативная память, %');
}

// Function to draw the chart
function drawChart(chart, data, label) {
    const datasets = serverNames.map((server, index) => ({
        label: server,
        data: data[server],
        borderColor: colors[index % colors.length],
        fill: false
    }));

    chart.data.labels = Array.from({ length: 10 }, (_, i) => i + 1);
    chart.data.datasets = datasets;
    chart.update();
}

// Create the charts
const cpuLoadChart = new Chart(document.getElementById('cpuLoadChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: [],
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            title: {
                display: true,
                text: 'Нагрузка ЦП, %'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        },
        animation: false
    }
});

const ramUsageChart = new Chart(document.getElementById('ramUsageChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: [],
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            title: {
                display: true,
                text: 'Оперативная память, %'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        },
        animation: false
    }
});


// Fetch server data every 5 seconds
setInterval(fetchServerData, 5000);

// Initial fetch
fetchServerData();
