function submitForm() {
    const imageName = document.getElementById('image_name').value;
    const imgFile = document.getElementById('img').files[0];

    if (!imageName || !imgFile) {
        alert('Please fill out all fields.');
        return;
    }

    const formData = new FormData();
    formData.append('image_name', imageName);
    formData.append('img', imgFile);

    fetch('/admin_panel/update_pages/update_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        alert(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while submitting the form.');
    });
}
