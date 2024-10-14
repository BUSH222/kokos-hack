async function send_to_server_btn(btn_type) {

    try {
        elem = document.getElementById('search_value').value
      const response = await fetch(window.location.href, {
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({'btn_type':btn_type,"search":elem}),
      });
      await response.json().then((value) => {
        window.location.href = value.re;
        });
    } catch (error) {
      console.error('Error: ', error);
    }
  }
 async function send_to_server_id(id) {
    try {
      const response = await fetch(window.location.href, {
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({'id':id}),
      });
      await response.json().then((value) => {
        window.location.href = value.re;
        });
    } catch (error) {
      console.error('Error: ', error);
    }
  }
