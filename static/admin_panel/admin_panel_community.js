
async function findUserData() {
    const username = document.getElementById('username').value;
    if (!username) {
        alert('Please enter a username.');
        return;
    }

    try {
        const response = await fetch(`/admin_panel/community/view_account_info?user=${username}`);
        const data = await response.json();

        if (data === 'No results') {
            alert('No user found with that username.');
            return;
        }

        document.getElementById('user-id').value = data[0];
        document.getElementById('name').value = data[1];
        document.getElementById('email').value = data[2];
        document.getElementById('password').value = data[3];
        document.getElementById('points').value = data[4];

        // Set roles checkboxes
        const roles = data[5].split(''); // Assuming roles are returned as a comma-separated string
        document.querySelectorAll('input[name="role"]').forEach(checkbox => {
            checkbox.checked = roles.includes(checkbox.value);
        });

        document.getElementById('user-data-section').style.display = 'block';
    } catch (error) {
        console.error('Error fetching user data:', error);
        alert('Error fetching user data.');
    }
}

async function updateUserData() {
    const uid = document.getElementById('user-id').value;
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const points = document.getElementById('points').value;

    // Collect roles
    const roles = Array.from(document.querySelectorAll('input[name="role"]:checked')).map(checkbox => checkbox.value).join('');

    try {
        const response = await fetch(`/admin_panel/community/set_account_info?user=${uid}&name=${name}&email=${email}&password=${password}&points=${points}&role=${roles}`);
        const result = await response.text();
        alert(result)
    } catch (error) {
        console.error('Error updating user data:', error);
        alert('Error updating user data.');
    }
}

async function deleteUser() {
    const uid = document.getElementById('user-id').value;

    try {
        const response = await fetch(`/admin_panel/community/delete_account?id=${uid}`);
        const result = await response.text();
        alert(result)
    } catch (error) {
        console.error('Error deleting user', error);
        alert('Error deleting user');
    }
}


async function pruneUser() {
    const uid = document.getElementById('user-id').value;

    try {
        const response = await fetch(`/admin_panel/community/prune_account?id=${uid}`);
        const result = await response.text();
        alert(result)
    } catch (error) {
        console.error('Error pruning user', error);
        alert('Error pruning user');
    }
}
