function sendRequest(url) {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.getElementById('result').innerHTML = data;
        })
        .catch(error => console.error('Error:', error));
}

function deleteAccount() {
    const user = document.getElementById('username').value;
    sendRequest(`/admin_panel/community/delete_account?user=${user}`);
}

function setRoles() {
    const user = document.getElementById('username').value;
    const roles = document.getElementById('roles').value;
    sendRequest(`/admin_panel/community/set_roles?user=${user}&roles=${roles}`);
}

function viewRoles() {
    const user = document.getElementById('username').value;
    sendRequest(`/admin_panel/community/view_roles?user=${user}`);
}

function viewActivityPoints() {
    const user = document.getElementById('username').value;
    sendRequest(`/admin_panel/community/view_activity_points?user=${user}`);
}

function setActivityPoints() {
    const user = document.getElementById('username').value;
    const points = document.getElementById('points').value;
    sendRequest(`/admin_panel/community/set_activity_points?user=${user}&points=${points}`);
}
