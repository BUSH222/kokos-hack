const cpuLoadData = {};
const ramUsageData = {};
const rpmData = {};
const serverNames = [];

const colors = ['#E60000', '#32CD32', '#0000FF']

const timeLabels = Array(10).fill('');

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
    const currentTime = new Date().toLocaleTimeString('en-GB', { hour12: false });

    if (timeLabels.length >= 10) {
        timeLabels.shift();
    }
    timeLabels.push(currentTime);

    for (const server in data) {
        if (data.hasOwnProperty(server)) {
            serverNames.push(server);
            if (!cpuLoadData[server]) {
                cpuLoadData[server] = Array(10).fill(null); // Initialize with 10 null values
                ramUsageData[server] = Array(10).fill(null); // Initialize with 10 null values
                rpmData[server] = Array(10).fill(null);
            }
            cpuLoadData[server].push(data[server].cpu);
            ramUsageData[server].push(data[server].ram);
            rpmData[server].push(data[server].rpm)

            // Limit to 10 data points
            if (cpuLoadData[server].length > 10) cpuLoadData[server].shift();
            if (ramUsageData[server].length > 10) ramUsageData[server].shift();
            if (rpmData[server].length > 10) rpmData[server].shift();
        }
    }

    // Redraw the charts with new data
    drawChart(cpuLoadChart, cpuLoadData, 'Нагрузка ЦП');
    drawChart(ramUsageChart, ramUsageData, 'Оперативная память');
    drawChart(rpmChart, rpmData, 'Оперативная память');
}

// Function to draw the chart
function drawChart(chart, data, label) {
    const datasets = serverNames.map((server, index) => ({
        label: server,
        data: data[server],
        borderColor: colors[index % colors.length],
        fill: false
    }));

    chart.data.labels = timeLabels;
    chart.data.datasets = datasets;
    chart.update();
}

// Create the charts
const cpuLoadChart = new Chart(document.getElementById('cpuLoadChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: timeLabels,
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            title: {
                display: false,
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            },
            x: {
                ticks: {
                    font: {
                        size: 10
                    }
                }
            }
        },
        animation: false
    }
});

const ramUsageChart = new Chart(document.getElementById('ramUsageChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: timeLabels,
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            title: {
                display: false,
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            },
            x: {
                ticks: {
                    font: {
                        size: 10
                    }
                }
            }
        },
        animation: false
    }
});

const rpmChart = new Chart(document.getElementById('rpmChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: timeLabels,
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            title: {
                display: false,
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 1000,
                type: 'logarithmic'
            },
            x: {
                ticks: {
                    font: {
                        size: 10
                    }
                }
            }
        },
        animation: false
    }
});

// Fetch server data every 5 seconds
setInterval(fetchServerData, 5000);

// Initial fetch
fetchServerData();
