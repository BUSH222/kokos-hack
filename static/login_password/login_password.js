async function send_to_server(btn_type) {
    try {
      const response = await fetch(window.location.href, {
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({'btn_type':btn_type}),
      });
    } catch (error) {
      console.error('Error: ', error);
    }
  }