function createGame() {
    const event_id = document.getElementById('event_id').value;
    const gameName = document.getElementById('game_name').value;
    const gameStartTime = document.getElementById('game_start_time').value;
    const gameEndTime = document.getElementById('game_end_time').value;
    const team1Name = document.getElementById('team1_name').value;
    const team2Name = document.getElementById('team2_name').value;
    const team1Score = document.getElementById('team1_score').value;
    const team2Score = document.getElementById('team2_score').value;
    const livestreamLink = document.getElementById('livestream_link').value;
    const videoLink = document.getElementById('video_link').value;
    const gameDescription = document.getElementById('game_description').value;
    const matchStatisticExternalLink = document.getElementById('match_statistic_external_link').value;

    // Prepare form data
    const formData = new FormData();

    let url;
    if (event_id == '') {
        formData.append('game_name', gameName);
        formData.append('game_start_time', gameStartTime);
        formData.append('game_end_time', gameEndTime);
        formData.append('team1_name', team1Name);
        formData.append('team2_name', team2Name);
        formData.append('team1_score', team1Score);
        formData.append('team2_score', team2Score);
        formData.append('livestream_link', livestreamLink);
        formData.append('video_link', videoLink);
        formData.append('game_description', gameDescription);
        formData.append('match_statistic_external_link', matchStatisticExternalLink);
        url = '/admin_panel/event_manager/new_event'; // New event
    } else {
        formData.append('event_id', event_id); // Add event_id for editing
        url = '/admin_panel/event_manager/edit_event'; // Edit event
    }
    // Send the request
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => alert(data))
    .catch(error => alert('Error: ' + error));
}


async function findEvent() {
    try {
        const event_id = document.getElementById('event_id').value;
        const response = await fetch(`/admin_panel/event_manager/get_event?event_id=${event_id}`);
        const data = await response.json();

        if (response.ok) {
            // Fill in the inputs with the retrieved data
            document.getElementById('game_name').value = data.game_name;
            document.getElementById('game_start_time').value = data.game_start_time;
            document.getElementById('game_end_time').value = data.game_end_time;
            document.getElementById('team1_name').value = data.team1_name;
            document.getElementById('team2_name').value = data.team2_name;
            document.getElementById('team1_score').value = data.team1_score;
            document.getElementById('team2_score').value = data.team2_score;
            document.getElementById('livestream_link').value = data.livestream_link;
            document.getElementById('video_link').value = data.video_link;
            document.getElementById('game_description').value = data.game_description;
            document.getElementById('match_statistic_external_link').value = data.match_statistic_external_link;
        } else {
            console.error('Error fetching event:', data.error || data);
            alert(`Error fetching event: ${data.error}`);
        }
    } catch (error) {
        console.error('Error fetching event:', error);
    }
}


function clearInputs() {
    document.getElementById('game_name').value = '';
    document.getElementById('game_start_time').value = '';
    document.getElementById('game_end_time').value = '';
    document.getElementById('team1_name').value = '';
    document.getElementById('team2_name').value = '';
    document.getElementById('team1_score').value = '';
    document.getElementById('team2_score').value = '';
    document.getElementById('livestream_link').value = '';
    document.getElementById('video_link').value = '';
    document.getElementById('game_description').value = '';
    document.getElementById('match_statistic_external_link').value = '';
}

function downloadTickets() {
    const event_id = document.getElementById('event_id').value;
    if (event_id == ''){
        alert('ID must not be empty.')
    }
    else{
        window.location.href = `/admin_panel/tickets?id=${event_id}`;
    }
}