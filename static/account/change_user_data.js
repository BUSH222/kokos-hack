async function send_to_server(btn_type) {
    try {
        name = document.getElementById('name').value
        fav_player = document.getElementById('fav_player').value
        about_me = document.getElementById('about_me').value
        vk_acc = document.getElementById('vk_acc').value
        telegram_acc = document.getElementById('telegram_acc').value
      const response = await fetch(window.location.href, {
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({'btn_type':btn_type , 'pb_id':elem,'name':name,'fav_player':'fav_player','about_me':about_me,'vk_acc':vk_acc,"telegram_acc":telegram_acc}),
      });
    } catch (error) {
      console.error('Error: ', error);
    }
  }