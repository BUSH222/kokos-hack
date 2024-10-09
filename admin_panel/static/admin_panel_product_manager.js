function createProduct() {
    const product_id = document.getElementById('product_id').value;
    const product_name = document.getElementById('product_name').value;
    const product_price = document.getElementById('product_price').value;
    const product_description = document.getElementById('product_description').value;
    const picture_url = document.getElementById('picture_url').value;

    // Prepare form data
    const formData = new FormData();

    let url;
    if (event_id == '') {
        formData.append('product_id', product_id);
        formData.append('product_name', product_name);
        formData.append('product_price', product_price);
        formData.append('product_description', product_description);
        formData.append('picture_url', picture_url);
        url = '/admin_panel/product_manager/new_product'; // New event
    } else {
        formData.append('event_id', event_id); // Add event_id for editing
        url = '/admin_panel/product_manager/edit_product'; // Edit event
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

function findProduct() {
    const product_id = document.getElementById('product_id').value;

    // Validate product ID
    if (product_id === '') {
        alert('Please enter a Product ID.');
        return;
    }

    // Send request to get product details
    fetch(`/admin_panel/product_manager/get_product?product_id=${product_id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Product not found');
            }
            return response.json();
        })
        .then(data => {
            // Populate form fields with product data
            document.getElementById('product_name').value = data.product_name;
            document.getElementById('product_price').value = data.product_price;
            document.getElementById('product_description').value = data.product_description;
            document.getElementById('picture_url').value = data.picture_url;
        })
        .catch(error => alert('Error: ' + error.message));
}

function deleteProduct() {
    const product_id = document.getElementById('product_id').value;

    // Validate product ID
    if (product_id === '') {
        alert('Please enter a Product ID to delete.');
        return;
    }

    // Send request to delete the product
    fetch(`/admin_panel/product_manager/delete_product?product_id=${product_id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error deleting product');
        }
        return response.text();
    })
    .then(data => {
        alert(data); // Notify user of success
        // Clear input fields after deletion if necessary
        clearInputs();
    })
    .catch(error => alert('Error: ' + error.message));
}

function clearInputs() {
    document.getElementById('product_id').value = '';
    document.getElementById('product_name').value = '';
    document.getElementById('product_price').value = '';
    document.getElementById('product_description').value = '';
    document.getElementById('picture_url').value = '';
}
