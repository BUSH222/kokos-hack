async function send_to_server_btn(btn_type) {

    try {
        search = document.getElementById('search_value').value
        tags = document.getElementById('tags_value').value
        news_time = document.getElementById('news_time_value').value
        pag = document.getElementById('pag_value').value
      const response = await fetch(window.location.href, {
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({'btn_type':btn_type,"search":search,"tag":tags,"news_time":news_time,"pag":pag}),
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
