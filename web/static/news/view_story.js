async function send_to_server_btn(btn_type) {

    try {
        comment_value = document.getElementById('comment_value').value
      const response = await fetch(window.location.href, {
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({'btn_type':btn_type,"comment_value":comment_value}),
      });
      await response.json().then((value) => {
        window.location.href = value.re;
        });
    } catch (error) {
      console.error('Error: ', error);
    }
  }