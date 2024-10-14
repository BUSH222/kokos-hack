async function send_to_server(btn_type) {
    try {
      const response = await fetch(window.location.href, {
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({'btn_type':btn_type}),
      });
      await response.json().then((value) => {
        window.location.href = value.re;
        });
    } catch (error) {
      console.error('Error: ', error);
    }
  }