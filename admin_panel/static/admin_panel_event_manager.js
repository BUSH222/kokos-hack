function createGame() {
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

    const url = `/admin_panel/event_manager/new_event?game_name=${gameName}&game_start_time=${gameStartTime}&game_end_time=${gameEndTime}&team1_name=${team1Name}&team2_name=${team2Name}&team1_score=${team1Score}&team2_score=${team2Score}&livestream_link=${livestreamLink}&video_link=${videoLink}&game_description=${gameDescription}&match_statistic_external_link=${matchStatisticExternalLink}`;

    fetch(url)
        .then(response => response.text())
        .then(data => alert(data))
        .catch(error => alert('Error: ' + error));
}
