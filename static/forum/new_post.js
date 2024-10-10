async function send_to_server_btn(btn_type) {

    try {

        tags = document.getElementById('tags_value').value
        title = document.getElementById('title_time_value').value
        post_text = document.getElementById('post_text_value').value
      const response = await fetch(window.location.href, {
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({'btn_type':btn_type,"tags":tags,"post_text":news_time,"title":title}),
      });
      await response.json().then((value) => {
        window.location.href = value.re;
        });
    } catch (error) {
      console.error('Error: ', error);
    }
  }